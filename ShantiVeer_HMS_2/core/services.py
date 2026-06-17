"""Database queries for dashboard and APIs."""
from datetime import timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone


def get_dashboard_stats():
    from opd.models import OPDVisit
    from income.models import IncomeEntry
    from uhid.models import Patient
    from ipd.models import IPDAdmission
    from core.models import Bed

    today = timezone.localdate()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    opd_today = OPDVisit.objects.filter(date=today).count()
    opd_week = OPDVisit.objects.filter(date__gte=week_ago).count()
    opd_month = OPDVisit.objects.filter(date__gte=month_ago).count()
    total_patients = Patient.objects.count()
    ipd_admitted = IPDAdmission.objects.filter(status='Admitted').count()

    # Billing stats
    total = IncomeEntry.objects.aggregate(s=Sum('amount'))['s'] or 0
    paid = IncomeEntry.objects.filter(payment_mode='Cash').aggregate(s=Sum('amount'))['s'] or 0
    today_income = IncomeEntry.objects.filter(date=today).aggregate(s=Sum('amount'))['s'] or 0

    # Average contact = total income / total visits (avoid division by zero)
    total_visits = OPDVisit.objects.count()
    avg_contact = (total / total_visits) if total_visits > 0 else 0

    # Bed stats
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(status='Occupied').count()

    return {
        'appointment_key': opd_today,
        'appointment_past': OPDVisit.objects.filter(date__lt=today).count(),
        'total_billing': f'{total:,.2f}',
        'collections': f'{paid:,.2f}',
        'today_income': f'{today_income:,.2f}',
        'rev_billing': f'{(total - paid):,.2f}',
        'avg_contact': f'{avg_contact:,.2f}',
        'appointments_month': opd_month,
        'appointments_week': opd_week,
        'total_patients': total_patients,
        'ipd_admitted': ipd_admitted,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'vacant_beds': total_beds - occupied_beds,
    }


def get_dashboard_beds():
    from core.models import Bed
    return [
        {
            'room': b.room_no,
            'bed_no': b.bed_no,
            'status': b.status,
            'occupied': b.occupied,
            'patient': b.patient_name,
        }
        for b in Bed.objects.select_related('patient').all()[:8]
    ]


def get_today_appointments():
    from opd.models import OPDVisit
    today = timezone.localdate()
    return [
        {
            'name': v.patient.name,
            'gender': v.patient.gender,
            'date': str(v.date),
            'doctor': v.doctor_name or '—',
            'opd_no': v.opd_no,
        }
        for v in OPDVisit.objects.filter(date=today).select_related('patient')[:10]
    ]


def get_emergency_patients():
    from ipd.models import IPDAdmission
    return [
        {'name': a.patient.name, 'date': str(a.date), 'category': a.category, 'ipd_no': a.ipd_no}
        for a in IPDAdmission.objects.filter(category='ICU', status='Admitted').select_related('patient')[:5]
    ]


def get_low_stock_medicines():
    from pharmacy.models import PharmacyItem
    from pharmacy.services import is_low_stock

    return [
        {
            'id': i.id,
            'name': i.name,
            'stock': i.stock,
            'buffer': i.buffer,
            'unit': i.unit_type,
            'urgency': 'critical' if i.stock == 0 else 'low',
        }
        for i in PharmacyItem.objects.filter(is_active=True)
        if is_low_stock(i)
    ]


def get_required_prescription_medicines():
    from prescription.models import PrescriptionMedicine

    lines = PrescriptionMedicine.objects.filter(
        status__in=[PrescriptionMedicine.STATUS_PENDING, PrescriptionMedicine.STATUS_LOW_STOCK],
    ).select_related('prescription__opd_visit__patient')[:15]

    return [
        {
            'id': line.id,
            'patient_name': line.prescription.patient.name,
            'uhid': line.prescription.patient.uhid,
            'opd_no': line.prescription.opd_visit.opd_no,
            'medicine': line.medicine_name,
            'quantity': line.quantity,
            'dosage': line.dosage,
            'status': line.get_status_display(),
            'visit_id': line.prescription.opd_visit_id,
            'stock': line.pharmacy_item.stock if line.pharmacy_item else None,
        }
        for line in lines
    ]


def get_recent_prescriptions():
    from prescription.models import Prescription

    return [
        {
            'id': p.opd_visit_id,
            'patient_name': p.patient.name,
            'uhid': p.patient.uhid,
            'opd_no': p.opd_visit.opd_no,
            'diagnosis': (p.diagnosis or '—')[:50],
            'updated': p.updated_at.strftime('%d-%m-%Y %H:%M'),
        }
        for p in Prescription.objects.select_related('opd_visit__patient').order_by('-updated_at')[:8]
    ]


def get_unread_notifications(user=None, limit=10):
    from core.models import Notification

    qs = Notification.objects.filter(is_read=False)
    if user and user.is_authenticated:
        qs = qs.filter(Q(user=user) | Q(user__isnull=True))
    return list(qs[:limit])


def get_unread_notification_count(user=None):
    from core.models import Notification

    qs = Notification.objects.filter(is_read=False)
    if user and user.is_authenticated:
        qs = qs.filter(Q(user=user) | Q(user__isnull=True))
    return qs.count()


def patient_to_dict(p):
    return {
        'uhid': p.uhid,
        'name': p.name,
        'gender': p.gender,
        'age': p.age_display,
        'mobile': p.mobile,
    }


def opd_to_dict(v):
    from prescription.models import Prescription
    pres = Prescription.objects.filter(opd_visit=v).first()
    return {
        'id': v.id,
        'opd_no': v.opd_no,
        'uhid': v.patient.uhid,
        'name': v.patient.name,
        'gender': v.patient.gender,
        'phone': v.patient.mobile,
        'date': str(v.date),
        'total': f'{v.total_amount:.2f}',
        'diagnosis': pres.diagnosis if pres else '',
        'medicines': pres.medicines if pres else '',
        'advice': pres.advice if pres else '',
    }