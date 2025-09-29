// Contextos dos gráficos
const ctxPrefeitura = document.getElementById('chartPrefeitura').getContext('2d');
const ctxConectada = document.getElementById('chartConectada').getContext('2d');

// Gráfico Prefeitura
const chartPrefeitura = new Chart(ctxPrefeitura, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Prefeitura',
            borderColor: 'rgb(0, 200, 0)',
            backgroundColor: 'rgba(0, 200, 0, 0.1)',
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

// Gráfico Conectada
const chartConectada = new Chart(ctxConectada, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Conectada',
            borderColor: 'rgb(0, 0, 255)',
            backgroundColor: 'rgba(0, 0, 255, 0.1)',
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

        // Atualiza Prefeitura
        chartPrefeitura.data.labels = data.ping.prefeitura.map(d => d.time);
        chartPrefeitura.data.datasets[0].data = data.ping.prefeitura.map(d => d.latency);
        chartPrefeitura.update();

        document.getElementById('prefeituraPing').innerText = data.ping.prefeitura.slice(-1)[0]?.latency || 0;
        document.getElementById('prefeituraDownload').innerText = data.ping.prefeitura.slice(-1)[0]?.download || 0;
        document.getElementById('prefeituraUpload').innerText = data.ping.prefeitura.slice(-1)[0]?.upload || 0;
        document.getElementById('prefeituraQuedas').innerText = data.stats.quedas_hoje;

        // Atualiza Conectada
        chartConectada.data.labels = data.ping.conectada.map(d => d.time);
        chartConectada.data.datasets[0].data = data.ping.conectada.map(d => d.latency);
        chartConectada.update();

        document.getElementById('conectadaPing').innerText = data.ping.conectada.slice(-1)[0]?.latency || 0;
        document.getElementById('conectadaDownload').innerText = data.ping.conectada.slice(-1)[0]?.download || 0;
        document.getElementById('conectadaUpload').innerText = data.ping.conectada.slice(-1)[0]?.upload || 0;
        document.getElementById('conectadaQuedas').innerText = data.stats.quedas_3dias;

    } catch (err) {
        console.error("Erro ao buscar dados:", err);
    }
}

setInterval(fetchData, 1000);
fetchData();
