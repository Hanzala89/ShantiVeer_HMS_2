from decimal import Decimal
from datetime import date, time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from uhid.models import Patient
from masterdata.models import Doctor, TestInterpretation
from opd.models import OPDVisit
from prescription.models import Prescription
from ipd.models import IPDAdmission, DischargeSummary, IPDPayment
from lab.models import LabTestMaster, LabInvestigation, LabInvestigationItem
from pharmacy.models import PharmacyItem, PharmacySale, PharmacyPurchase
from income.models import IncomeEntry
from core.models import Bed


class Command(BaseCommand):
    help = 'Seed HMS database with demo data'

    def handle(self, *args, **options):
        # Ensure permanent admin credentials
        User.objects.get_or_create(username='admin', defaults={'email': 'kaifrana219@gmail.com'})
        u = User.objects.get(username='admin')
        u.email = 'kaifrana219@gmail.com'
        u.set_password('admin@123')

        u.is_staff = u.is_superuser = True
        u.save()

        if Patient.objects.exists():
            self.stdout.write('Data exists — skipping seed (delete DB to re-seed)')
            return

        patients = [
            Patient.objects.create(uhid='3491', name='Naveen Jain', gender='Male', mobile='9811256863', age_years=35, address='Delhi'),
            Patient.objects.create(uhid='3490', name='AMIR ALAM', gender='Male', mobile='9012409842', age_years=21, address='Noida'),
            Patient.objects.create(uhid='3489', name='VIVEK TYAGI', gender='Male', mobile='9876543210', age_years=32, address='Gurgaon'),
            Patient.objects.create(uhid='3492', name='Priya Singh', gender='Female', mobile='9988776655', age_years=28, address='Delhi'),
        ]

        Doctor.objects.bulk_create([
            Doctor(name='Dr. Neha Sharma', department='General Medicine', specialization='Physician', phone='9876543210'),
            Doctor(name='Dr. Rajesh Kumar', department='Orthopedics', specialization='Orthopedic', phone='9876543211'),
        ])

        for p, fees, dt in zip(patients[:3], [500, 300, 500], [date(2026, 5, 1), date(2026, 6, 8), date(2026, 6, 7)]):
            v = OPDVisit.objects.create(
                patient=p, date=dt, time=time(10, 0), doctor_name='Dr. Neha Sharma',
                fees=Decimal(fees), total_amount=Decimal(fees),
            )
            Prescription.objects.create(
                opd_visit=v,
                diagnosis='Fever' if p.name == 'AMIR ALAM' else '',
                medicines='Tab Paracetamol 500mg' if p.name == 'AMIR ALAM' else '',
            )

        for p, room, cat, diag in [
            (patients[0], '101', 'General', 'Typhoid'),
            (patients[2], '205', 'PRIVATE', 'Fracture'),
            (patients[1], 'ICU01', 'ICU', 'Pneumonia'),
        ]:
            IPDAdmission.objects.create(
                patient=p, date=date(2026, 6, 1), consultant='Dr. Neha Sharma',
                room_no=room, category=cat, diagnosis=diag, status='Admitted',
            )

        tests = [('ESR', 100), ('AEC', 150), ('CBC', 250), ('KFT', 500), ('LFT', 450)]
        LabTestMaster.objects.bulk_create([LabTestMaster(name=n, rate=Decimal(r)) for n, r in tests])

        inv = LabInvestigation.objects.create(
            patient=patients[1], patient_name='Mr. AMIR ALAM', mobile='9012409842',
            test_date=date(2026, 6, 9), total=Decimal('1000'), payment_mode='Cash',
        )
        for t in LabTestMaster.objects.filter(name__in=['KFT', 'CBC']):
            LabInvestigationItem.objects.create(investigation=inv, test=t, rate=t.rate, quantity=1, amount=t.rate)

        PharmacyItem.objects.bulk_create([
            PharmacyItem(name='MEDICINE TEST 2', schedule='SCHEDULE A', unit_type='TAB', hsn='3006 (9% + 9%)', packing=10, buffer=20, stock=5, sale_price=25),
            PharmacyItem(name='PARACIP 1000MG IV', schedule='SCHEDULE E1', unit_type='INJ', hsn='3004 (6% + 6%)', packing=1, buffer=15, stock=8, sale_price=80),
            PharmacyItem(name='CROSIN TAB', schedule='--NA--', unit_type='TAB', hsn='3004 (6% + 6%)', packing=10, buffer=25, stock=200, sale_price=15),
        ])

        from prescription.models import PrescriptionMedicine
        from pharmacy.services import sync_pharmacy_stock_notifications, notify_prescription_medicine
        paracip = PharmacyItem.objects.filter(name__icontains='PARACIP').first()
        pres = Prescription.objects.first()
        if pres and paracip:
            line = PrescriptionMedicine.objects.create(
                prescription=pres, medicine_name='PARACIP 1000MG IV',
                dosage='1-0-1 x 3 days', quantity=5, pharmacy_item=paracip,
                status=PrescriptionMedicine.STATUS_LOW_STOCK,
            )
            notify_prescription_medicine(line)
        sync_pharmacy_stock_notifications()

        IncomeEntry.objects.create(
            date=date(2026, 6, 9), category='Investigation', patient_name='Mr. AMIR ALAM',
            description='KIDNEY FUNCTION TEST (KFT), COMPLETE BLOOD COUNT (CBC)',
            payment_mode='Cash', amount=Decimal('1000'),
        )
        IncomeEntry.objects.create(
            date=date(2026, 6, 9), category='Investigation', patient_name='Mr. Naveen Jain',
            description='ESR, AEC', payment_mode='Cash', amount=Decimal('80'),
        )

        Bed.objects.bulk_create([
            Bed(room_no='101', bed_no='B1', status='Occupied', patient=patients[0]),
            Bed(room_no='102', bed_no='B2', status='Vacant'),
            Bed(room_no='ICU01', bed_no='B1', status='Occupied', patient=patients[1]),
            Bed(room_no='205', bed_no='B1', status='Occupied', patient=patients[2]),
        ])

        TestInterpretation.objects.create(
            test_name='NT-PRO-BETA NATRIURETIC PEPTIDE (NT-PRO-BNP)',
            interpretation='NT-Pro BNP values increase with age. CHF classification levels apply.',
            status='Active',
        )

        self.stdout.write(self.style.SUCCESS('Database seeded! Login: admin / admin123'))
