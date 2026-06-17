/**
 * SantiVeer HMS — Dashboard JS
 * Handles chart rendering and filter tab interactions.
 * NOTE: window.DASHBOARD_API must be set before this script runs,
 * OR this script defers initialization until DOMContentLoaded.
 */

(function () {
    'use strict';

    var chartInstances = {};

    function getApiUrl() {
        return window.DASHBOARD_API || '/api/dashboard/';
    }

    function destroyChart(id) {
        if (chartInstances[id]) {
            chartInstances[id].destroy();
            delete chartInstances[id];
        }
    }

    function getDefaultData() {
        return {
            patient_chart: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                patient: [40, 55, 45, 70, 60, 80, 75],
                trend: [35, 50, 48, 65, 58, 72, 70],
                patient_trends: [30, 45, 50, 60, 55, 68, 65],
            },
            patient_pie: { old: 65, new: 35 },
            revenue: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                values: [800, 1200, 900, 1500, 1100, 1700, 1300],
            },
            emergency: { values: [2, 3, 5, 8, 12, 15, 18] },
        };
    }

    /* ===== Chart renderers ===== */

    function renderPatientChart(data) {
        var el = document.getElementById('patientChart');
        if (!el) return;
        destroyChart('patientChart');
        chartInstances['patientChart'] = new Chart(el, {
            type: 'line',
            data: {
                labels: data.patient_chart.labels,
                datasets: [
                    {
                        label: 'Patients',
                        data: data.patient_chart.patient,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59,130,246,0.08)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 5,
                    },
                    {
                        label: 'Trend',
                        data: data.patient_chart.trend,
                        borderColor: '#ec4899',
                        borderDash: [5, 4],
                        tension: 0.4,
                        pointRadius: 2,
                        fill: false,
                    },
                    {
                        label: 'Patient Trends',
                        data: data.patient_chart.patient_trends,
                        borderColor: '#eab308',
                        tension: 0.4,
                        pointRadius: 2,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } },
                    tooltip: { mode: 'index', intersect: false },
                },
                scales: {
                    y: { beginAtZero: true, ticks: { font: { size: 10 } } },
                    x: { ticks: { font: { size: 10 }, maxRotation: 45 } },
                },
            },
        });
    }

    function renderPieChart(data) {
        var el = document.getElementById('patientPieChart');
        if (!el) return;
        destroyChart('patientPieChart');
        chartInstances['patientPieChart'] = new Chart(el, {
            type: 'doughnut',
            data: {
                labels: ['Old Patients', 'New Patients'],
                datasets: [{
                    data: [data.patient_pie.old, data.patient_pie.new],
                    backgroundColor: ['#3b82f6', '#22c55e'],
                    borderWidth: 2,
                }],
            },
            options: {
                cutout: '65%',
                plugins: {
                    legend: { position: 'bottom', labels: { font: { size: 9 } } },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                var total = ctx.dataset.data.reduce(function (a, b) { return a + b; }, 0);
                                var pct = total ? Math.round(ctx.parsed / total * 100) : 0;
                                return ctx.label + ': ' + ctx.parsed + ' (' + pct + '%)';
                            }
                        }
                    }
                },
            },
        });
    }

    function renderRevenueChart(data) {
        var el = document.getElementById('revenueChart');
        if (!el) return;
        destroyChart('revenueChart');
        chartInstances['revenueChart'] = new Chart(el, {
            type: 'bar',
            data: {
                labels: data.revenue.labels,
                datasets: [{
                    label: 'Revenue (₹)',
                    data: data.revenue.values,
                    backgroundColor: 'rgba(6,182,212,0.7)',
                    borderColor: '#06b6d4',
                    borderWidth: 1,
                    borderRadius: 4,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return '₹' + Number(ctx.parsed.y).toLocaleString('en-IN');
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            font: { size: 10 },
                            callback: function (v) {
                                return '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v);
                            }
                        }
                    },
                    x: { ticks: { font: { size: 10 } } }
                },
            },
        });
    }

    function renderEmergencyChart(data) {
        var el = document.getElementById('emergencyChart');
        if (!el) return;
        destroyChart('emergencyChart');
        chartInstances['emergencyChart'] = new Chart(el, {
            type: 'line',
            data: {
                labels: ['', '', '', '', '', '', ''],
                datasets: [{
                    data: data.emergency.values,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239,68,68,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 3,
                }],
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { x: { display: false }, y: { display: false } },
            },
        });
    }

    function renderMiniCharts() {
        ['apptTrendChart', 'miniMonthChart'].forEach(function (id) {
            var el = document.getElementById(id);
            if (!el) return;
            destroyChart(id);
            chartInstances[id] = new Chart(el, {
                type: 'line',
                data: {
                    labels: ['', '', '', ''],
                    datasets: [{
                        data: [10, 25, 15, 30],
                        borderColor: '#22c55e',
                        tension: 0.4,
                        pointRadius: 0,
                    }],
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { display: false } },
                },
            });
        });
    }

    function renderAll(data) {
        renderPatientChart(data);
        renderPieChart(data);
        renderRevenueChart(data);
        renderEmergencyChart(data);
        renderMiniCharts();
    }

    /* ===== Fetch helpers ===== */

    function fetchStats(range, callback) {
        var url = getApiUrl() + '?range=' + encodeURIComponent(range || 'month');
        fetch(url)
            .then(function (r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(callback)
            .catch(function (err) {
                console.warn('Dashboard API error:', err);
                callback(getDefaultData());
            });
    }

    /* ===== Filter tab wiring ===== */

    function setActiveTab(container, selectedBtn) {
        container.querySelectorAll('button').forEach(function (b) {
            b.classList.remove('active');
        });
        selectedBtn.classList.add('active');
    }

    function setupFilterTabs(containerId, onSelect) {
        var container = document.getElementById(containerId);
        if (!container) return;

        container.querySelectorAll('button[data-range]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                setActiveTab(container, this);
                var range = this.getAttribute('data-range');
                // Show loading state on button
                var origText = this.textContent;
                this.textContent = '...';
                var self = this;
                fetchStats(range, function (data) {
                    self.textContent = origText;
                    onSelect(data);
                });
            });
        });
    }

    /* ===== Init ===== */

    function init() {
        // Read the initially active range from the button, default to 'month'
        var patientContainer = document.getElementById('patientChartFilters');
        var initialRange = 'month';
        if (patientContainer) {
            var activeBtn = patientContainer.querySelector('button.active[data-range]');
            if (activeBtn) initialRange = activeBtn.getAttribute('data-range');
        }

        // Initial full render
        fetchStats(initialRange, renderAll);

        // Patient chart filter tabs
        setupFilterTabs('patientChartFilters', function (data) {
            renderPatientChart(data);
        });

        // Billing/Revenue filter tabs
        setupFilterTabs('billingFilters', function (data) {
            renderRevenueChart(data);
        });
    }

    // Wait for full DOM + scripts
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOMContentLoaded already fired (e.g. script is deferred/async)
        init();
    }

})();