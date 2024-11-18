const apiKey = 'bd5e378503939ddaee76f12ad7a97608';
const locationSelect = document.getElementById('location-select');

// Funzione per ottenere le previsioni meteo
async function fetchWeather(locationId) {
    try {
        const response = await fetch(`https://api.openweathermap.org/data/2.5/forecast?id=${locationId}&units=metric&appid=${apiKey}`);
        const data = await response.json();
        return data.list.map(entry => ({
            time: entry.dt_txt,
            temp: entry.main.temp,
            rain: entry.rain ? entry.rain['3h'] || 0 : 0,
            snow: entry.snow ? entry.snow['3h'] || 0 : 0
        }));
    } catch (error) {
        console.error('Errore nel recupero dei dati meteo:', error);
        return [];
    }
}

// Funzione per aggiornare il grafico con ECharts
function updateChart(forecast) {
    const times = forecast.map(entry => entry.time);
    const temps = forecast.map(entry => entry.temp);
    const rains = forecast.map(entry => entry.rain);
    const snows = forecast.map(entry => entry.snow);

    const chart = echarts.init(document.getElementById('weather-chart'));

    const options = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['Temperatura (°C)', 'Pioggia (mm)', 'Neve (mm)']
        },
        xAxis: {
            type: 'category',
            data: times,
            boundaryGap: false,
            axisLabel: {
                rotate: 45
            }
        },
        yAxis: [
            {
                type: 'value',
                name: 'Temperatura (°C)',
                min: Math.min(...temps) - 2,
                max: Math.max(...temps) + 2
            },
            {
                type: 'value',
                name: 'Pioggia/Neve (mm)',
                min: 0,
                max: Math.max(Math.max(...rains), Math.max(...snows)) + 2,
                axisLabel: {
                    formatter: '{value} mm'
                }
            }
        ],
        series: [
            {
                name: 'Temperatura (°C)',
                type: 'line',
                data: temps,
                smooth: true,
                color: '#ff6347'
            },
            {
                name: 'Pioggia (mm)',
                type: 'line',
                yAxisIndex: 1,
                data: rains,
                smooth: true,
                color: '#4682b4'
            },
            {
                name: 'Neve (mm)',
                type: 'line',
                yAxisIndex: 1,
                data: snows,
                smooth: true,
                color: '#00bfff'
            }
        ]
    };

    chart.setOption(options);
}

// Carica i dati iniziali per Milano
async function initializeWidget() {
    const initialForecast = await fetchWeather(locationSelect.value);
    updateChart(initialForecast);
}

// Cambia località quando l'utente seleziona un'altra città
locationSelect.addEventListener('change', async () => {
    const forecast = await fetchWeather(locationSelect.value);
    updateChart(forecast);
});

window.onload = function() {
    initializeWidget();
};
