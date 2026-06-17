from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from uhid.models import Patient
from .models import LabTestMaster, LabInvestigation, LabInvestigationItem


@login_required
def investigation(request):
    if request.method == 'POST':
        patient = None
        uhid = request.POST.get('uhid')
        if uhid:
            patient = Patient.objects.filter(uhid=uhid).first()

        inv = LabInvestigation.objects.create(
            patient=patient,
            patient_name=request.POST.get('patient_name', ''),
            mobile=request.POST.get('mobile', ''),
            address=request.POST.get('address', ''),
            consultant=request.POST.get('consultant', '-- Self --'),
            referred_by=request.POST.get('referred', 'SELF'),
            remarks=request.POST.get('remarks', ''),
            discount=Decimal(request.POST.get('discount') or 0),
            payment_mode=request.POST.get('payment_mode', 'Cash'),
            test_date=request.POST.get('date') or timezone.localdate(),
        )
        total = Decimal(0)
        for test_id in request.POST.getlist('tests'):
            test = LabTestMaster.objects.filter(pk=test_id).first()
            if test:
                qty = int(request.POST.get(f'qty_{test_id}', 1))
                item = LabInvestigationItem.objects.create(
                    investigation=inv, test=test, rate=test.rate, quantity=qty,
                )
                total += item.amount
        inv.total = total - inv.discount
        inv.save()

        from income.models import IncomeEntry
        IncomeEntry.objects.create(
            date=inv.test_date, category='Investigation', patient_name=inv.patient_name,
            description=f'Lab Bill {inv.bill_no}', payment_mode=inv.payment_mode, amount=inv.total,
        )
        messages.success(request, f'Lab bill {inv.bill_no} submitted.')
        return redirect('lab:view_all')

    return render(request, 'lab/investigation.html', {
        'active_sidebar': 'lab',
        'tests': LabTestMaster.objects.filter(is_active=True),
        'today': timezone.localdate().isoformat(),
    })


@login_required
def view_all(request):
    q = request.GET.get('q', '').strip()
    reports = LabInvestigation.objects.prefetch_related('items__test')
    if q:
        reports = reports.filter(Q(bill_no__icontains=q) | Q(patient_name__icontains=q))
    data = [{
        'id': r.id, 'bill_no': r.bill_no, 'patient': r.patient_name,
        'tests': ', '.join(i.test.name for i in r.items.all()),
        'amount': r.total, 'date': str(r.test_date),
    } for r in reports[:50]]
    return render(request, 'lab/view_all.html', {'active_sidebar': 'lab', 'reports': data, 'q': q})


@login_required
def view_report(request, pk):
    inv = get_object_or_404(LabInvestigation.objects.prefetch_related('items__test'), pk=pk)
    report = {
        'bill_no': inv.bill_no, 'patient': inv.patient_name, 'date': str(inv.test_date),
        'test_results': [{'name': i.test.name, 'result': 'Normal', 'unit': '-', 'ref': 'Within range'} for i in inv.items.all()],
    }
    return render(request, 'lab/view_report.html', {'active_sidebar': 'lab', 'report': report})


@login_required
def test_list(request):
    tests = LabTestMaster.objects.all().order_by('name')
    return render(request, 'lab/test_list.html', {
        'active_sidebar': 'lab',
        'tests': tests,
    })


@login_required
def test_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        rate = request.POST.get('rate', '0').strip()
        if name:
            if LabTestMaster.objects.filter(name__iexact=name).exists():
                messages.error(request, f'Test "{name}" already exists.')
            else:
                LabTestMaster.objects.create(name=name, rate=rate or 0)
                messages.success(request, f'Test "{name}" added successfully.')
                return redirect('lab:test_list')
        else:
            messages.error(request, 'Test name is required.')
    return render(request, 'lab/test_form.html', {
        'active_sidebar': 'lab',
        'action': 'Add',
        'obj': None,
    })


@login_required
def test_edit(request, pk):
    test = get_object_or_404(LabTestMaster, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        rate = request.POST.get('rate', '0').strip()
        if name:
            test.name = name
            test.rate = rate or 0
            test.save()
            messages.success(request, f'Test "{name}" updated.')
            return redirect('lab:test_list')
        else:
            messages.error(request, 'Test name is required.')
    return render(request, 'lab/test_form.html', {
        'active_sidebar': 'lab',
        'action': 'Edit',
        'obj': test,
    })


@login_required
def test_toggle(request, pk):
    test = get_object_or_404(LabTestMaster, pk=pk)
    test.is_active = not test.is_active
    test.save()
    status = 'activated' if test.is_active else 'deactivated'
    messages.success(request, f'Test "{test.name}" {status}.')
    return redirect('lab:test_list')