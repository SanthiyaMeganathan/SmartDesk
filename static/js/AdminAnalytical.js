document.addEventListener("DOMContentLoaded", function () {
    

    const barCtx = document.getElementById('barChart').getContext('2d');
    new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: chartData.labels, 
            datasets: [{
                data: chartData.barData, 
                backgroundColor: '#3b82f6', 
                hoverBackgroundColor: '#3b82f6',
                borderRadius: 4,
                barPercentage: 0.8,
                categoryPercentage: 0.9
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 0,
                    bottom: 0
                }
            },
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 30, 
                    ticks: { 
                        stepSize: 5, 
                        color: '#9ca3af', 
                        font: {size: 11},
                        padding: 8 
                    },
                    grid: { 
                        display: true, 
                        color: '#e5e7eb',
                        drawTicks: false 
                    },
                    border: { display: true, color: '#e5e7eb' }
                },
                x: {
                    ticks: { 
                        color: '#9ca3af', 
                        font: {size: 11},
                        padding: 8 
                    },
                    grid: { 
                        display: true, 
                        color: '#e5e7eb',
                        drawTicks: false 
                    },
                    border: { display: true, color: '#e5e7eb' }
                }
            }
        }
    });

    const donutCtx = document.getElementById('donutChart').getContext('2d');
    new Chart(donutCtx, {
        type: 'doughnut',
        data: {
            labels: ['Network', 'Access', 'Software', 'Hardware'],
            datasets: [{
                data: chartData.donutData, 
                backgroundColor: ['#3b82f6', '#f59e0b', '#ef4444', '#10b981'],
                borderWidth: 0,
                cutout: '75%' 
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            }
        }
    });

    const lineCtx = document.getElementById('lineChart').getContext('2d');
    new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: chartData.labels, 
            datasets: [
                {
                    label: 'Open',
                    data: chartData.lineOpen, 
                    borderColor: '#ef4444', 
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4, 
                    pointRadius: 4,
                    pointBackgroundColor: '#ef4444',
                    fill: true 
                },
                {
                    label: 'Resolved',
                    data: chartData.lineResolved, 
                    borderColor: '#10b981', 
                    backgroundColor: 'rgba(16, 185, 129, 0.1)', 
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#10b981',
                    fill: true 
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 20,
                    ticks: { 
                        stepSize: 4, 
                        color: '#9ca3af', 
                        font: {size: 11} 
                    },
                    grid: { color: '#f3f4f6' },
                    border: { display: false }
                },
                x: {
                    ticks: { color: '#9ca3af', font: {size: 11} },
                    grid: { display: true, color: '#f3f4f6' },
                    border: { display: false }
                }
            }
        }
    });
});