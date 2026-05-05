// dashboard-charts.js - Gráficos del dashboard

// Inicializar todos los gráficos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    
    // Verificar que Chart.js está cargado
    if (typeof Chart === 'undefined') {
        console.error('Chart.js no está cargado');
        return;
    }
    
    // ============================================
    // GRÁFICO 1: Reservas últimos 7 días
    // ============================================
    const reservasChart = document.getElementById('reservasChart');
    if (reservasChart) {
        new Chart(reservasChart.getContext('2d'), {
            type: 'line',
            data: {
                labels: window.dashboardData?.dias_labels || [],
                datasets: [{
                    label: 'Reservas',
                    data: window.dashboardData?.reservas_data || [],
                    borderColor: '#ef233c',
                    backgroundColor: 'rgba(239, 35, 60, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }
    
    // ============================================
    // GRÁFICO 2: Top servicios
    // ============================================
    const topServiciosChart = document.getElementById('topServiciosChart');
    if (topServiciosChart) {
        new Chart(topServiciosChart.getContext('2d'), {
            type: 'bar',
            data: {
                labels: window.dashboardData?.servicios_labels || [],
                datasets: [{
                    label: 'Cantidad de reservas',
                    data: window.dashboardData?.servicios_data || [],
                    backgroundColor: '#4361ee',
                    borderRadius: 8
                }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }
    
    // ============================================
    // GRÁFICO 3: Reservas por mes
    // ============================================
    const reservasMesChart = document.getElementById('reservasMesChart');
    if (reservasMesChart) {
        new Chart(reservasMesChart.getContext('2d'), {
            type: 'bar',
            data: {
                labels: window.dashboardData?.meses_labels || [],
                datasets: [{
                    label: 'Reservas por mes',
                    data: window.dashboardData?.reservas_mes_data || [],
                    backgroundColor: '#28a745',
                    borderRadius: 8
                }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }
    
    // ============================================
    // GRÁFICO 4: Ingresos por mes (NUEVO)
    // ============================================
    const ingresosChart = document.getElementById('ingresosChart');
    if (ingresosChart) {
        new Chart(ingresosChart.getContext('2d'), {
            type: 'line',
            data: {
                labels: window.dashboardData?.meses_labels || [],
                datasets: [{
                    label: 'Ingresos ($)',
                    data: window.dashboardData?.ingresos_por_mes || [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }
    
    // ============================================
    // GRÁFICO 5: Top clientes (NUEVO)
    // ============================================
    const topClientesChart = document.getElementById('topClientesChart');
    if (topClientesChart) {
        new Chart(topClientesChart.getContext('2d'), {
            type: 'bar',
            data: {
                labels: window.dashboardData?.clientes_nombres || [],
                datasets: [{
                    label: 'Reservas realizadas',
                    data: window.dashboardData?.clientes_cantidades || [],
                    backgroundColor: '#fd7e14',
                    borderRadius: 8
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }
    
    // ============================================
    // GRÁFICO 6: Estado de reservas (Doughnut)
    // ============================================
    const estadosChart = document.getElementById('estadosChart');
    if (estadosChart) {
        new Chart(estadosChart.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Pendientes', 'Confirmados', 'Cancelados'],
                datasets: [{
                    data: [
                        window.dashboardData?.estado_pendiente || 0,
                        window.dashboardData?.estado_confirmado || 0,
                        window.dashboardData?.estado_cancelado || 0
                    ],
                    backgroundColor: ['#f59e0b', '#28a745', '#dc3545'],
                    borderRadius: 8
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
    
    // ============================================
    // GRÁFICO 7: Próximos 7 días (NUEVO)
    // ============================================
    const proximosDiasChart = document.getElementById('proximosDiasChart');
    if (proximosDiasChart) {
        new Chart(proximosDiasChart.getContext('2d'), {
            type: 'line',
            data: {
                labels: window.dashboardData?.proximos_dias_labels || [],
                datasets: [{
                    label: 'Reservas',
                    data: window.dashboardData?.proximos_dias_data || [],
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }
    
    console.log('✅ Todos los gráficos del dashboard inicializados');
});