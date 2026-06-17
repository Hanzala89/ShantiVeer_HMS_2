from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Patient


@login_required
def update(request):
    search_uhid = request.GET.get('uhid', '')
    patient = None
    if search_uhid:
        patient = Patient.objects.filter(uhid=search_uhid).first()

    if request.method == 'POST':
        uhid = request.POST.get('uhid') or search_uhid
        p, _ = Patient.objects.get_or_create(uhid=uhid, defaults={'name': request.POST.get('patient_name', ''), 'mobile': request.POST.get('mobile', '')})
        p.title = request.POST.get('title', p.title)
        p.name = request.POST.get('patient_name', p.name)
        p.gender = request.POST.get('gender', p.gender)
        p.marital_status = request.POST.get('marital', p.marital_status)
        p.mobile = request.POST.get('mobile', p.mobile)
        p.blood_group = request.POST.get('blood_group', p.blood_group)
        p.address = request.POST.get('address', p.address)
        if request.POST.get('dob'):
            p.dob = request.POST.get('dob')
        p.save()
        messages.success(request, 'UHID record saved.')
        return redirect('uhid:update')

    patients = Patient.objects.all()
    page = Paginator(patients, 10).get_page(request.GET.get('page', 1))

    return render(request, 'uhid/update.html', {
        'active_sidebar': 'uhid',
        'patients': page,
        'search_uhid': search_uhid,
        'patient': patient or {},
    })
