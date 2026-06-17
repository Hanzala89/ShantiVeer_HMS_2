from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from uhid.models import Patient
from .models import OPDVisit
from prescription.models import Prescription


@login_required
def registration(request):

    now = timezone.localtime()
    edit_id = request.GET.get('edit')

    if request.method == 'POST':
        uhid = request.POST.get('uhid', '').strip()

        # If this is an edit, update existing visit instead of creating a new one.
        edit_id = request.GET.get('edit')
        visit_obj = None
        if edit_id:
            visit_obj = get_object_or_404(OPDVisit, pk=edit_id)

        if uhid:
            patient, _ = Patient.objects.get_or_create(
                uhid=uhid,
                defaults={
                    'name': request.POST.get('patient_name', ''),
                    'mobile': request.POST.get('phone', ''),
                    'gender': request.POST.get('gender', 'Male'),
                    'address': request.POST.get('address', ''),
                },
            )
        else:
            patient = Patient.objects.create(
                name=request.POST.get('patient_name', ''),
                mobile=request.POST.get('phone', ''),
                gender=request.POST.get('gender', 'Male'),
                address=request.POST.get('address', ''),
                age_years=int(request.POST.get('age') or 0),
            )

        # Update patient fields
        patient.name = request.POST.get('patient_name', patient.name)
        patient.mobile = request.POST.get('phone', patient.mobile)
        patient.gender = request.POST.get('gender', patient.gender)
        patient.address = request.POST.get('address', patient.address)
        if request.POST.get('age'):
            patient.age_years = int(request.POST.get('age'))
        patient.save()

        if visit_obj:
            # Update existing visit
            visit_obj.patient = patient
            visit_obj.date = request.POST.get('date') or now.date()
            visit_obj.time = request.POST.get('time') or now.time()
            visit_obj.referral = request.POST.get('referral', '')
            visit_obj.doctor_name = request.POST.get('doctor', '')
            visit_obj.fees = Decimal(request.POST.get('fees') or 0)
            visit_obj.discount = Decimal(request.POST.get('discount') or 0)
            visit_obj.head = request.POST.get('head', 'Opd Consultation')
            visit_obj.payment_mode = request.POST.get('payment_mode', 'Cash')
            visit_obj.reference_info = request.POST.get('reference', '')
            visit_obj.save()
            Prescription.objects.get_or_create(opd_visit=visit_obj)
            messages.success(request, f'OPD {visit_obj.opd_no} updated successfully.')
        else:
            # Create new visit
            visit_obj = OPDVisit.objects.create(
                patient=patient,
                date=request.POST.get('date') or now.date(),
                time=request.POST.get('time') or now.time(),
                referral=request.POST.get('referral', ''),
                doctor_name=request.POST.get('doctor', ''),
                fees=Decimal(request.POST.get('fees') or 0),
                discount=Decimal(request.POST.get('discount') or 0),
                head=request.POST.get('head', 'Opd Consultation'),
                payment_mode=request.POST.get('payment_mode', 'Cash'),
                reference_info=request.POST.get('reference', ''),
            )
            Prescription.objects.get_or_create(opd_visit=visit_obj)
            messages.success(request, f'OPD {visit_obj.opd_no} saved successfully.')

        return redirect('prescription:list')

    next_no = f'OPD{OPDVisit.objects.count() + 1:03d}'
    initial = {}
    if edit_id:
        v = get_object_or_404(OPDVisit, pk=edit_id)
        initial = {'patient': v.patient, 'visit': v}

    return render(request, 'opd/registration.html', {
        'active_sidebar': 'opd',
        'opd_no': next_no,
        'today': now.date().isoformat(),
        'now_time': now.strftime('%H:%M'),
        'initial': initial,
    })


@login_required
@require_POST
def delete_opd_visit(request, pk):
    visit = get_object_or_404(OPDVisit, pk=pk)
    visit.delete()
    messages.success(request, f'OPD {visit.opd_no} deleted successfully.')
    return redirect('prescription:list')

