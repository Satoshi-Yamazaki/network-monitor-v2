const ctx = document.getElementById('pingChart').getContext('2d');

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Ping (ms)',
            borderColor: 'rgb(0, 200, 255)',
            backgroundColor: 'rgba(0, 200, 255, 0.1)',
            data: [],
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

        // Atualiza gráfico
        chart.data.labels = data.ping.map(d => d.time);
        chart.data.datasets[0].data = data.ping.map(d => d.latency);
        chart.update();

        // Atualiza estatísticas
        document.getElementById('currentPing').innerText = data.current_ping;
        document.getElementById('downloadSpeed').innerText = data.download;
        document.getElementById('uploadSpeed').innerText = data.upload;
        document.getElementById('quedasHoje').innerText = data.stats.quedas_hoje;
        document.getElementById('quedas3dias').innerText = data.stats.quedas_3dias;
        document.getElementById('quedasTotal').innerText = data.stats.quedas_total;
    } catch (err) {
        console.error("Erro ao buscar dados:", err);
    }
}

setInterval(fetchData, 1000);
fetchData();
