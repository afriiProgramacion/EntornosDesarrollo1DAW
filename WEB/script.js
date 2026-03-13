// 1. Configuración inicial del mapa centrado en Andalucía
const map = L.map('map').setView([37.3891, -4.7794], 7);

// 2. Capa de mapa oscura (Gratis y sin necesidad de registro)
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO'
}).addTo(map);

// Grupo para gestionar los marcadores de los aviones
let planesGroup = L.layerGroup().addTo(map);

// 3. Función que genera el icono del avión rotado
const createPlaneIcon = (course) => L.divIcon({
    html: `<svg style="transform: rotate(${course}deg); width: 30px; height: 30px;" viewBox="0 0 24 24">
            <path fill="#22d3ee" stroke="white" stroke-width="0.5" d="M21,16V14L13,9V3.5A1.5,1.5 0 0,0 11.5,2A1.5,1.5 0 0,0 10,3.5V9L2,14V16L10,13.5V19L8,20.5V22L11.5,21L15,22V20.5L13,19V13.5L21,16Z" />
           </svg>`,
    className: "", // Quitamos estilos por defecto de Leaflet
    iconSize: [30, 30],
    iconAnchor: [15, 15]
});

// 4. Función principal: Consultar la API de OpenSky
async function updatePlanes() {
    // Coordenadas de la "caja" que envuelve Andalucía
    const url = 'https://opensky-network.org/api/states/all?lamin=35.7&lomin=-7.6&lamax=38.8&lomax=-1.6';
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        // Borramos los aviones antiguos para dibujar los nuevos
        planesGroup.clearLayers();

        if (data.states && data.states.length > 0) {
            data.states.forEach(plane => {
                // Desestructuramos los datos de la API
                const [icao, callsign, country, time, last, lon, lat, alt, ground, vel, course] = plane;

                if (lat && lon) {
                    // Creamos el marcador con el icono rotado según el rumbo (course)
                    const marker = L.marker([lat, lon], {
                        icon: createPlaneIcon(course || 0)
                    });

                    // Información que sale al hacer click
                    const info = `
                        <div style="text-align:center">
                            <b style="color:#22d3ee; font-size:14px;">VUELO: ${callsign || 'N/A'}</b><br>
                            <hr style="border:0; border-top:1px solid #334155; margin:5px 0">
                            Altitud: ${Math.round(alt)} m<br>
                            Velocidad: ${Math.round(vel * 3.6)} km/h<br>
                            Origen: ${country}
                        </div>
                    `;

                    marker.bindPopup(info);
                    planesGroup.addLayer(marker);
                }
            });
            document.getElementById('counter').innerText = data.states.length + " AVIONES";
        } else {
            document.getElementById('counter').innerText = "0 AVIONES";
        }
    } catch (error) {
        console.error("Error al obtener datos:", error);
        document.getElementById('counter').innerText = "ERROR DE CONEXIÓN";
    }
}

// Actualizar cada 10 segundos (para no bloquear la API gratuita)
updatePlanes();
setInterval(updatePlanes, 10000);