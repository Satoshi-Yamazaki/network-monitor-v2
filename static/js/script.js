async function fetchData() {
    try {
        const res = await fetch('/data');
        const data = await res.json();

        // Substitui 0 por null para falhas, mantendo o tempo
        const prefeituraPingData = data.prefeitura.ping.map(d => ({
            time: d.time,
            latency: d.latency > 0 ? d.latency : null
        }));
        const conectadaPingData = data.conectada.ping.map(d => ({
            time: d.time,
            latency: d.latency > 0 ? d.latency : null
        }));

        // Atualiza Prefeitura
        chartPrefeitura.data.labels = prefeituraPingData.map(d => d.time);
        chartPrefeitura.data.datasets[0].data = prefeituraPingData.map(d => d.latency);
        chartPrefeitura.update();

        // Atualiza Conectada
        chartConectada.data.labels = conectadaPingData.map(d => d.time);
        chartConectada.data.datasets[0].data = conectadaPingData.map(d => d.latency);
        chartConectada.update();

        // Atualiza estatísticas, substituindo 0 ou null por '--'
        document.getElementById('currentPingPrefeitura').innerText = data.prefeitura.current_ping > 0 ? data.prefeitura.current_ping : '--';
        document.getElementById('downloadSpeedPrefeitura').innerText = data.prefeitura.download > 0 ? data.prefeitura.download : '--';
        document.getElementById('uploadSpeedPrefeitura').innerText = data.prefeitura.upload > 0 ? data.prefeitura.upload : '--';

        document.getElementById('currentPingConectada').innerText = data.conectada.current_ping > 0 ? data.conectada.current_ping : '--';
        document.getElementById('downloadSpeedConectada').innerText = data.conectada.download > 0 ? data.conectada.download : '--';
        document.getElementById('uploadSpeedConectada').innerText = data.conectada.upload > 0 ? data.conectada.upload : '--';

    } catch (err) {
        console.error("Erro ao buscar dados:", err);
    }
}

setInterval(fetchData, 1000);
fetchData();
