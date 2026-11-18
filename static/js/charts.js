/**
 * Smart Civic Issue System - Chart.js Visualizations
 */

let statusChartInstance = null;
let categoryChartInstance = null;
let monthlyTrendChartInstance = null;
let departmentChartInstance = null;

function initDashboardCharts() {
    fetch('/api/dashboard-charts/')
        .then(response => response.json())
        .then(data => {
            renderStatusChart(data.status_labels, data.status_data);
            renderCategoryChart(data.categories);
            renderMonthlyTrendChart(data.months, data.filed_series, data.resolved_series);
            renderDepartmentChart(data.dept_names, data.dept_assigned, data.dept_resolved);
        })
        .catch(err => console.error('Error fetching dashboard chart data:', err));
}

function getThemeFontColor() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    return isDark ? '#94a3b8' : '#64748b';
}

function getThemeGridColor() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    return isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.06)';
}

function renderStatusChart(labels, values) {
    const ctx = document.getElementById('statusDonutChart');
    if (!ctx) return;

    if (statusChartInstance) statusChartInstance.destroy();

    const colors = [
        '#64748b', // Submitted (grey)
        '#0284c7', // Under Review (sky)
        '#2563eb', // Assigned (blue)
        '#d97706', // In Progress (amber)
        '#10b981', // Resolved (green)
        '#ef4444', // Rejected (red)
    ];

    statusChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#131b2e' : '#ffffff',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getThemeFontColor(),
                        padding: 14,
                        font: { size: 12, weight: 500 }
                    }
                }
            },
            cutout: '68%'
        }
    });
}

function renderCategoryChart(categories) {
    const ctx = document.getElementById('categoryBarChart');
    if (!ctx) return;

    if (categoryChartInstance) categoryChartInstance.destroy();

    const labels = categories.map(c => c.name);
    const data = categories.map(c => c.count);
    const colors = categories.map(c => c.color || '#0d9488');

    categoryChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Complaints',
                data: data,
                backgroundColor: colors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: getThemeFontColor(),
                        font: { size: 11 },
                        maxRotation: 45,
                        minRotation: 20
                    }
                },
                y: {
                    grid: { color: getThemeGridColor() },
                    ticks: {
                        color: getThemeFontColor(),
                        stepSize: 1,
                        precision: 0
                    }
                }
            }
        }
    });
}

function renderMonthlyTrendChart(months, filed, resolved) {
    const ctx = document.getElementById('monthlyTrendChart');
    if (!ctx) return;

    if (monthlyTrendChartInstance) monthlyTrendChartInstance.destroy();

    monthlyTrendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Issues Filed',
                    data: filed,
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.1)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointBackgroundColor: '#0284c7',
                    pointRadius: 4
                },
                {
                    label: 'Issues Resolved',
                    data: resolved,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointBackgroundColor: '#10b981',
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: { color: getThemeFontColor(), font: { size: 12, weight: 600 } }
                }
            },
            scales: {
                x: {
                    grid: { color: getThemeGridColor() },
                    ticks: { color: getThemeFontColor() }
                },
                y: {
                    grid: { color: getThemeGridColor() },
                    ticks: {
                        color: getThemeFontColor(),
                        stepSize: 1,
                        precision: 0
                    }
                }
            }
        }
    });
}

function renderDepartmentChart(names, assigned, resolved) {
    const ctx = document.getElementById('departmentWorkloadChart');
    if (!ctx) return;

    if (departmentChartInstance) departmentChartInstance.destroy();

    departmentChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: names,
            datasets: [
                {
                    label: 'Assigned',
                    data: assigned,
                    backgroundColor: '#2563eb',
                    borderRadius: 6
                },
                {
                    label: 'Resolved',
                    data: resolved,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: getThemeFontColor() }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: getThemeFontColor() }
                },
                y: {
                    grid: { color: getThemeGridColor() },
                    ticks: {
                        color: getThemeFontColor(),
                        stepSize: 1,
                        precision: 0
                    }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('statusDonutChart')) {
        initDashboardCharts();
    }
});

// Re-render when theme changes to keep colors crisp
document.addEventListener('themeChanged', function () {
    if (document.getElementById('statusDonutChart')) {
        initDashboardCharts();
    }
});
