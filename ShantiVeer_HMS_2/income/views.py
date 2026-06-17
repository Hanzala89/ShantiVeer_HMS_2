from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from .models import IncomeEntry


@login_required
def daybook(request):
    selected = request.GET.get('date', timezone.localdate().isoformat())
    entries = IncomeEntry.objects.filter(date=selected)
    if not entries.exists():
        # Don't slice before further filtering/aggregation.
        entries = IncomeEntry.objects.all()[:20]
        entries = IncomeEntry.objects.filter(id__in=entries.values('id'))


    def fmt(qs, mode):
        return qs.filter(payment_mode=mode).aggregate(s=Sum('amount'))['s'] or 0

    totals = {
        'cash': f'{fmt(entries, "Cash"):,.2f}',
        'online': f'{fmt(entries, "UPI"):,.2f}',
        'card': f'{fmt(entries, "Card"):,.2f}',
        'cheque': f'{fmt(entries, "Cheque"):,.2f}',
        'income': f'{entries.aggregate(s=Sum("amount"))["s"] or 0:,.2f}',
    }

    data = [{
        'date': e.date.strftime('%d-%b-%Y'),
        'category': e.category,
        'patient': e.patient_name,
        'description': e.description,
        'mode': e.payment_mode,
        'amount': f'{e.amount:,.2f}',
    } for e in entries]

    return render(request, 'income/daybook.html', {
        'active_sidebar': 'income',
        'selected_date': selected,
        'entries': data,
        'totals': totals,
    })
