const ctxPrefeitura = document.getElementById('pingChartPrefeitura').getContext('2d');
const ctxConectada = document.getElementById('pingChartConectada').getContext('2d');

const chartPrefeitura = new Chart(ctxPrefeitura, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Prefeitura',
            borderColor: 'green',
            backgroundColor: 'rgba(0,255,0,0.1)',
            data: [],
            spanGaps: true,
            tension: 0.2
        }]
    },
    options: {
        animation: false,
        scales: {
            x: { ticks: { color: '#ccc' } },
            y: { ticks: { color: '#ccc' }, beginAtZero: true }
        }
    }
});

const chartConectada = new Chart(ctxConectada, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Conectada',
            borderColor: 'blue',
            backgroundColor: 'rgba(0,0,255,0.1)',
            data: [],
            spanGaps: true,
            tension: 0.2
        }]
    },
    options: {
        animation: false,
        scales: {
            x: { ticks: { color: '#ccc' } },
            y: { ticks: { color: '#ccc' }, beginAtZero: true }
        }
    }
});

async function fetchData() {
    try {
        const res = await fetch('/data');
        const data = await res.json();

        // Converte latência 0 em null para não quebrar o gráfico
        const prefeituraPingData = data.prefeitura.ping.map(d => d.latency > 0 ? d.latency : null);
        const conectadaPingData = data.conectada.ping.map(d => d.latency > 0 ? d.latency : null);

        // Atualiza Prefeitura
        chartPrefeitura.data.labels = data.prefeitura.ping.map(d => d.time);
        chartPrefeitura.data.datasets[0].data = prefeituraPingData;
        chartPrefeitura.update();

        // Atualiza Conectada
        chartConectada.data.labels = data.conectada.ping.map(d => d.time);
        chartConectada.data.datasets[0].data = conectadaPingData;
        chartConectada.update();

        // Atualiza estatísticas Prefeitura
        document.getElementById('currentPingPrefeitura').innerText = data.prefeitura.current_ping > 0 ? data.prefeitura.current_ping : '--';
        document.getElementById('downloadSpeedPrefeitura').innerText = data.prefeitura.download > 0 ? data.prefeitura.download : '--';
        document.getElementById('uploadSpeedPrefeitura').innerText = data.prefeitura.upload > 0 ? data.prefeitura.upload : '--';
        document.getElementById('quedasPrefeitura').innerText = data.prefeitura.stats.quedas_total || '--';

        // Atualiza estatísticas Conectada
        document.getElementById('currentPingConectada').innerText = data.conectada.current_ping > 0 ? data.conectada.current_ping : '--';
        document.getElementById('downloadSpeedConectada').innerText = data.conectada.download > 0 ? data.conectada.download : '--';
        document.getElementById('uploadSpeedConectada').innerText = data.conectada.upload > 0 ? data.conectada.upload : '--';
        document.getElementById('quedasConectada').innerText = data.conectada.stats.quedas_total || '--';

    } catch (err) {
        console.error("Erro ao buscar dados:", err);
        // Se falhar, mantém gráficos com null e stats como "--"
    }
}

setInterval(fetchData, 1000);
fetchData();
