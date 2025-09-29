const ctxPrefeitura = document.getElementById('pingChartPrefeitura').getContext('2d');
const ctxConectada = document.getElementById('pingChartConectada').getContext('2d');

const chartPrefeitura = new Chart(ctxPrefeitura, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Prefeitura', borderColor: 'green', backgroundColor: 'rgba(0,255,0,0.1)', data: [], tension: 0.2 }] },
    options: { animation: false, scales: { x: { ticks: { color: '#ccc' } }, y: { ticks: { color: '#ccc' }, beginAtZero: true } } }
});

const chartConectada = new Chart(ctxConectada, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Conectada', borderColor: 'blue', backgroundColor: 'rgba(0,0,255,0.1)', data: [], tension: 0.2 }] },
    options: { animation: false, scales: { x: { ticks: { color: '#ccc' } }, y: { ticks: { color: '#ccc' }, beginAtZero: true } } }
});

async function fetchData() {
    try {
        const res = await fetch('/data');
        const data = await res.json();

        // Atualiza Prefeitura
        chartPrefeitura.data.labels = data.prefeitura.ping.map(d => d.time);
        chartPrefeitura.data.datasets[0].data = data.prefeitura.ping.map(d => d.latency);
        chartPrefeitura.update();

        // Atualiza Conectada
        chartConectada.data.labels = data.conectada.ping.map(d => d.time);
        chartConectada.data.datasets[0].data = data.conectada.ping.map(d => d.latency);
        chartConectada.update();

        // Atualiza estatísticas
        document.getElementById('currentPingPrefeitura').innerText = data.prefeitura.current_ping;
        document.getElementById('downloadSpeedPrefeitura').innerText = data.prefeitura.download;
        document.getElementById('uploadSpeedPrefeitura').innerText = data.prefeitura.upload;

        document.getElementById('currentPingConectada').innerText = data.conectada.current_ping;
        document.getElementById('downloadSpeedConectada').innerText = data.conectada.download;
        document.getElementById('uploadSpeedConectada').innerText = data.conectada.upload;

    } catch (err) {
        console.error("Erro ao buscar dados:", err);
    }
}

setInterval(fetchData, 1000);
fetchData();
