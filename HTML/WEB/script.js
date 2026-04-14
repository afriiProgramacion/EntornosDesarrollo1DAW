// Centramos el mapa de aviones en Andalucía
const map = L.map('map').setView([37.1, -4.5], 7);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: 'Radar Aéreo'
}).addTo(map);

let planesGroup = L.layerGroup().addTo(map);

const createPlaneIcon = (course) => L.divIcon({
    html: `<svg style="transform: rotate(${course}deg); width: 25px; height: 25px;" viewBox="0 0 24 24">
            <path fill="#22d3ee" stroke="white" stroke-width="0.5" d="M21,16V14L13,9V3.5A1.5,1.5 0 0,0 11.5,2A1.5,1.5 0 0,0 10,3.5V9L2,14V16L10,13.5V19L8,20.5V22L11.5,21L15,22V20.5L13,19V13.5L21,16Z" />
           </svg>`,
    className: "",
    iconSize: [25, 25],
    iconAnchor: [12, 12]
});

async function updatePlanes() {
    const url = 'https://opensky-network.org/api/states/all?lamin=35.5&lomin=-7.6&lamax=38.8&lomax=-1.5';
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        planesGroup.clearLayers();

        if (data.states) {
            data.states.forEach(plane => {
                const [icao, callsign, country, time, last, lon, lat, alt, ground, vel, course] = plane;
                if (lat && lon) {
                    const marker = L.marker([lat, lon], { icon: createPlaneIcon(course || 0) });
                    marker.bindPopup(`<b>VUELO:</b> ${callsign || 'N/A'}<br><b>ALT:</b> ${Math.round(alt)}m`);
                    planesGroup.addLayer(marker);
                }
            });
            document.getElementById('counter').innerText = data.states.length + " AVIONES DETECTADOS";
        }
    } catch (e) {
        document.getElementById('counter').innerText = "ERROR SCANNER";
    }
}

updatePlanes();
setInterval(updatePlanes, 10000);