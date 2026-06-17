// Global HMS frontend helpers
document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
        if (!confirm(el.dataset.confirm || 'Are you sure?')) e.preventDefault();
    });
});

// Lab test checkbox -> selected table
document.querySelectorAll('.test-checkbox').forEach(cb => {
    cb.addEventListener('change', function () {
        const table = document.getElementById('selectedTestsBody');
        if (!table) return;
        const name = this.dataset.name;
        const rate = this.dataset.rate;
        if (this.checked) {
            const row = document.createElement('tr');
            row.dataset.test = name;
            row.innerHTML = `<td>${name}</td><td>${rate}</td><td><input type="number" value="1" min="1" class="form-control form-control-sm test-qty" style="width:60px"></td><td class="test-amt">${rate}</td><td><button type="button" class="btn btn-sm btn-danger remove-test">×</button></td>`;
            table.appendChild(row);
            row.querySelector('.remove-test').onclick = () => { row.remove(); this.checked = false; updateLabTotal(); };
            row.querySelector('.test-qty').oninput = updateLabTotal;
        } else {
            table.querySelector(`tr[data-test="${name}"]`)?.remove();
        }
        updateLabTotal();
    });
});

function updateLabTotal() {
    let total = 0;
    document.querySelectorAll('#selectedTestsBody tr').forEach(row => {
        const rate = parseFloat(row.cells[1].textContent) || 0;
        const qty = parseInt(row.querySelector('.test-qty')?.value) || 1;
        const amt = rate * qty;
        row.querySelector('.test-amt').textContent = amt;
        total += amt;
    });
    const totalEl = document.getElementById('labTotal');
    const dueEl = document.getElementById('labDue');
    const disc = parseFloat(document.getElementById('labDiscount')?.value) || 0;
    if (totalEl) totalEl.textContent = total;
    if (dueEl) dueEl.value = Math.max(0, total - disc);
}

if (document.getElementById('labDiscount')) {
    document.getElementById('labDiscount').addEventListener('input', updateLabTotal);
}
