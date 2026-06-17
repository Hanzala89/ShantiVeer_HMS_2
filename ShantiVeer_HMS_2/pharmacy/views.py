from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render

from .models import PharmacyItem, PharmacyPurchase, PharmacySale
from .services import sync_pharmacy_stock_notifications


@login_required
def items(request):
    if request.method == 'POST':
        PharmacyItem.objects.create(
            name=request.POST.get('name', ''),
            drug=request.POST.get('drug', ''),
            unit_type=request.POST.get('unit', 'TAB'),
            buffer=int(request.POST.get('buffer') or 20),
            schedule=request.POST.get('schedules', '--NA--'),
            packing=int(request.POST.get('packing') or 1),
            discount_on_sale='discount' in request.POST,
        )
        sync_pharmacy_stock_notifications()
        messages.success(request, 'Item added.')
        return redirect('pharmacy:items')

    q = request.GET.get('q', '').strip()
    qs = PharmacyItem.objects.filter(is_active=True)
    if q:
        qs = qs.filter(name__icontains=q)

    sync_pharmacy_stock_notifications()
    return render(
        request,
        'pharmacy/items.html',
        {
            'active_sidebar': 'pharmacy',
            'items': qs,
            'low_stock': [i for i in qs if i.stock <= i.buffer],
        },
    )


@login_required
def purchase(request):
    if request.method == 'POST':
        item_name = (request.POST.get('item_name') or '').strip()
        item_pk = request.POST.get('item')

        if item_name:
            item, _created = PharmacyItem.objects.get_or_create(
                name=item_name,
                defaults={
                    'drug': '',
                    'unit_type': 'TAB',
                    'buffer': 20,
                    'schedule': '--NA--',
                    'packing': 1,
                },
            )
        else:
            item = PharmacyItem.objects.get(pk=item_pk)

        qty = int(request.POST.get('qty') or 0)
        if qty <= 0:
            messages.error(request, 'Qty must be greater than 0.')
            return render(
                request,
                'pharmacy/purchase.html',
                {'active_sidebar': 'pharmacy', 'items': PharmacyItem.objects.filter(is_active=True)},
            )

        rate = Decimal(request.POST.get('rate') or 0)

        with transaction.atomic():
            item_locked = PharmacyItem.objects.select_for_update().get(pk=item.pk)
            PharmacyPurchase.objects.create(
                item=item_locked,
                supplier=request.POST.get('supplier', ''),
                quantity=qty,
                rate=rate,
            )
            item_locked.stock = item_locked.stock + qty
            item_locked.save(update_fields=['stock'])

        sync_pharmacy_stock_notifications()
        messages.success(request, 'Purchase recorded.')

    return render(
        request,
        'pharmacy/purchase.html',
        {'active_sidebar': 'pharmacy', 'items': PharmacyItem.objects.filter(is_active=True)},
    )


@login_required
def sale(request):
    if request.method == 'POST':
        item_pk = request.POST.get('item')
        item_text = (request.POST.get('item_text') or '').strip()
        qty = int(request.POST.get('qty') or 1)


        if qty <= 0:
            messages.error(request, 'Qty must be greater than 0.')
            return redirect('pharmacy:sale')

        item = None
        # Existing flow: item PK from dropdown
        if item_pk:
            try:
                item = PharmacyItem.objects.get(pk=item_pk)
            except PharmacyItem.DoesNotExist:
                item = None

        # New flow: resolve from typed text
        if item is None and item_text:
            item = PharmacyItem.objects.filter(name__iexact=item_text, is_active=True).first()
            if item is None:
                item = PharmacyItem.objects.filter(name__icontains=item_text, is_active=True).order_by('name').first()

        if item is None:
            messages.error(request, 'Item not found. Please check the item name.')
            return redirect('pharmacy:sale')

        with transaction.atomic():

            item_locked = PharmacyItem.objects.select_for_update().get(pk=item.pk)
            if item_locked.stock < qty:
                messages.error(
                    request,
                    f'Insufficient stock for {item_locked.name}. Available: {item_locked.stock}, Required: {qty}.',
                )
                return redirect('pharmacy:sale')

            amount = item_locked.sale_price * qty
            PharmacySale.objects.create(
                item=item_locked,
                patient_ref=request.POST.get('patient', ''),
                quantity=qty,
                amount=amount,
                payment_mode=request.POST.get('mode', 'Cash'),
            )
            item_locked.stock = item_locked.stock - qty
            item_locked.save(update_fields=['stock'])

        sync_pharmacy_stock_notifications()
        messages.success(request, 'Sale completed.')

    return render(
        request,
        'pharmacy/sale.html',
        {'active_sidebar': 'pharmacy', 'items': PharmacyItem.objects.filter(is_active=True)},
    )


@login_required
def sale_purchase(request):
    sales = [
        {
            'date': s.sold_at.date(),
            'type': 'Sale',
            'item': s.item.name,
            'qty': s.quantity,
            'amount': s.amount,
        }
        for s in PharmacySale.objects.select_related('item').order_by('-sold_at')[:20]
    ]
    purchases = [
        {
            'date': p.purchased_at.date(),
            'type': 'Purchase',
            'item': p.item.name,
            'qty': p.quantity,
            'amount': p.rate * p.quantity,
        }
        for p in PharmacyPurchase.objects.select_related('item').order_by('-purchased_at')[:20]
    ]
    records = sorted(sales + purchases, key=lambda x: x['date'], reverse=True)
    return render(
        request,
        'pharmacy/sale_purchase.html',
        {'active_sidebar': 'pharmacy', 'records': records},
    )

