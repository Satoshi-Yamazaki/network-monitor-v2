const ctxPrefeitura = document.getElementById('chartPrefeitura').getContext('2d');
const ctxConectada = document.getElementById('chartConectada').getContext('2d');

const chartPrefeitura = new Chart(ctxPrefeitura, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Prefeitura', borderColor: 'green', backgroundColor: 'rgba(0,255,0,0.1)', data: [], spanGaps: true, tension: 0.2 }] },
    options: { animation: false, scales: { x: { ticks: { color: '#ccc' } }, y: { ticks: { color: '#ccc' }, beginAtZero: true } } }
});

const chartConectada = new Chart(ctxConectada, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Conectada', borderColor: 'blue', backgroundColor: 'rgba(0,0,255,0.1)', data: [], spanGaps: true, tension: 0.2 }] },
    options: { animation: false, scales: { x: { ticks: { color: '#ccc' } }, y: { ticks: { color: '#ccc' }, beginAtZero: true } } }
});

async function fetchData() {
    try {
        const res = await fetch('/data');
        const data = await res.json();

        // Mantém o tempo mas transforma latência 0 em null
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

        // Atualiza estatísticas
        document.getElementById('prefeituraPing').innerText = data.prefeitura.current_ping > 0 ? data.prefeitura.current_ping : '--';
        document.getElementById('prefeituraDownload').innerText = data.prefeitura.download > 0 ? data.prefeitura.download : '--';
        document.getElementById('prefeituraUpload').innerText = data.prefeitura.upload > 0 ? data.prefeitura.upload : '--';

        document.getElementById('conectadaPing').innerText = data.conectada.current_ping > 0 ? data.conectada.current_ping : '--';
        document.getElementById('conectadaDownload').innerText = data.conectada.download > 0 ? data.conectada.download : '--';
        document.getElementById('conectadaUpload').innerText = data.conectada.upload > 0 ? data.conectada.upload : '--';

    } catch (err) {
        console.error("Erro ao buscar dados:", err);
    }
}

setInterval(fetchData, 1000);
fetchData();
