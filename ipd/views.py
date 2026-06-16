from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from uhid.models import Patient
from .models import IPDAdmission, IPDPayment, IPDMedicineLine, DischargeSummary


def _ipd_dict(a):
    return {
        'id': a.id,
        'name': a.patient.name,
        'age': a.patient.age_years,
        'gender': a.patient.gender.upper(),
        'uhid': a.patient.uhid,
        'ipd_no': a.ipd_no,
        'consultant': a.consultant,
        'room': a.room_no,
        'diagnosis': a.diagnosis,
        'date': str(a.date),
        'status': a.status,
        'category': a.category,
    }


@login_required
def patient_list(request):
    q = request.GET.get('q', '').strip()
    qs = IPDAdmission.objects.select_related('patient').filter(status='Admitted')
    if q:
        qs = qs.filter(Q(patient__name__icontains=q) | Q(ipd_no__icontains=q) | Q(patient__uhid__icontains=q))
    return render(request, 'ipd/patient_list.html', {'active_sidebar': 'ipd', 'patients': [_ipd_dict(a) for a in qs]})


@login_required
def admission(request):
    if request.method == 'POST':
        uhid = request.POST.get('uhid')
        patient = Patient.objects.filter(uhid=uhid).first() if uhid else None
        if not patient:
            patient = Patient.objects.create(
                name=request.POST.get('patient_name', ''),
                mobile=request.POST.get('contact', ''),
                gender=request.POST.get('gender', 'Male').title(),
                age_years=int(request.POST.get('age') or 0),
                address=request.POST.get('address', ''),
            )
        IPDAdmission.objects.create(
            patient=patient,
            date=request.POST.get('date') or timezone.localdate(),
            guardian=request.POST.get('guardian', ''),
            category=request.POST.get('category', 'General'),
            consultant=request.POST.get('consultant', ''),
            kyc_type=request.POST.get('kyc_type', ''),
            kyc_no=request.POST.get('kyc_no', ''),
            room_category=request.POST.get('room_category', ''),
            room_no=request.POST.get('room_no', ''),
            diagnosis=request.POST.get('diagnosis', ''),
            tpa=request.POST.get('tpa', ''),
            policy_no=request.POST.get('policy_no', ''),
            insurance_co=request.POST.get('insurance', ''),
            referral=request.POST.get('referral', ''),
            status=request.POST.get('status', 'Admitted'),
        )
        messages.success(request, 'IPD admission saved.')
        return redirect('ipd:patient_list')

    present = IPDAdmission.objects.filter(status='Admitted').select_related('patient')
    present_list = [{'name': a.patient.name, 'room': a.room_no, 'ipd_no': a.ipd_no, 'category': a.category} for a in present]

    return render(request, 'ipd/admission.html', {
        'active_sidebar': 'ipd',
        'ipd_no': f'IPD{IPDAdmission.objects.count() + 101}',
        'today': timezone.localdate().isoformat(),
        'present_patients': present_list,
    })


@login_required
def payment(request):
    if request.method == 'POST':
        adm = IPDAdmission.objects.filter(ipd_no=request.POST.get('ipd_no')).first()
        if adm:
            IPDPayment.objects.create(
                admission=adm,
                amount=Decimal(request.POST.get('amount') or 0),
                payment_mode=request.POST.get('mode', 'Cash'),
                remarks=request.POST.get('remarks', ''),
            )
            messages.success(request, 'Payment recorded.')
    payments = IPDPayment.objects.select_related('admission__patient').order_by('-paid_at')[:20]
    data = [{'ipd_no': p.admission.ipd_no, 'name': p.admission.patient.name, 'amount': p.amount, 'mode': p.payment_mode, 'date': p.paid_at.date()} for p in payments]
    return render(request, 'ipd/payment.html', {'active_sidebar': 'ipd', 'payments': data})


@login_required
def bill(request):
    bill_data = None
    ipd_no = request.GET.get('ipd_no')
    if ipd_no:
        adm = IPDAdmission.objects.filter(ipd_no=ipd_no).first()
        if adm:
            items = [{'desc': 'Room Charges', 'amount': '7500'}, {'desc': 'Consultation', 'amount': '2000'}]
            med_total = sum(m.amount for m in adm.medicine_lines.all())
            if med_total:
                items.append({'desc': 'Medicines', 'amount': str(med_total)})
            bill_data = {'items': items, 'total': sum(Decimal(i['amount']) for i in items)}
    return render(request, 'ipd/bill.html', {'active_sidebar': 'ipd', 'bill': bill_data})


@login_required
def discharge_list(request):
    q = request.GET.get('q', '').strip()
    items = DischargeSummary.objects.select_related('admission__patient')
    if q:
        items = items.filter(Q(admission__ipd_no__icontains=q) | Q(admission__patient__name__icontains=q))
    discharges = [{
        'id': d.id, 'ipd_no': d.admission.ipd_no, 'name': d.admission.patient.name,
        'age': d.admission.patient.age_years, 'gender': d.admission.patient.gender,
        'guardian': d.admission.guardian, 'room': d.admission.room_no,
        'contact': d.admission.patient.mobile, 'consultant': d.admission.consultant,
        'discharge_date': str(d.discharge_date),
    } for d in items]
    return render(request, 'ipd/discharge_list.html', {'active_sidebar': 'ipd', 'discharges': discharges, 'q': q})


@login_required
def discharge_add(request):
    if request.method == 'POST':
        adm = IPDAdmission.objects.filter(ipd_no=request.POST.get('ipd_no')).first()
        if adm:
            DischargeSummary.objects.get_or_create(
                admission=adm,
                defaults={'discharge_date': request.POST.get('discharge_date') or timezone.localdate()},
            )
            adm.status = 'Discharged'
            adm.save()
            messages.success(request, 'Discharge added.')
        return redirect('ipd:discharge_list')
    return redirect('ipd:discharge_list')


@login_required
def discharge_print(request, pk):
    d = get_object_or_404(DischargeSummary.objects.select_related('admission__patient'), pk=pk)
    return render(request, 'prescription/print.html', {
        'record': {'name': d.admission.patient.name, 'opd_no': d.admission.ipd_no, 'date': str(d.discharge_date), 'diagnosis': d.admission.diagnosis, 'medicines': 'Follow up in 7 days', 'advice': d.notes},
    })


@login_required
def medicine(request):
    if request.method == 'POST':
        adm = IPDAdmission.objects.filter(
            ipd_no=request.POST.get('ipd_no')
        ).first()

        if adm:
            IPDMedicineLine.objects.create(
                admission=adm,
                medicine_name=request.POST.get('medicine', ''),
                quantity=int(request.POST.get('qty') or 1),
                rate=Decimal(request.POST.get('rate') or 0),
            )
            messages.success(request, 'Medicine added.')

    lines = IPDMedicineLine.objects.select_related(
        'admission'
    ).order_by('-id')[:20]

    medicines = [
        {
            'name': m.medicine_name,
            'qty': m.quantity,
            'rate': m.rate,
            'amount': m.amount
        }
        for m in lines
    ]

    return render(
        request,
        'ipd/medicine.html',
        {
            'active_sidebar': 'ipd',
            'medicines': medicines
        }
    )


@login_required
def delete_patient(request, pk):
    admission = get_object_or_404(IPDAdmission, pk=pk)

    if request.method == "POST":
        admission.delete()
        messages.success(
            request,
            "Patient deleted successfully."
        )

    return redirect('ipd:patient_list')