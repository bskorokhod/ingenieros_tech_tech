// creo el ícono del pin
const icono_pin = L.icon({
    iconUrl: '../static/icons/location-dot-verde.svg',
    iconSize: [30, 30]
});

// inicializo el mapa
let mapa = L.map('map', { attributionControl: false }).setView([-34.617777, -58.368758], 16);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    minZoom: 9,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(mapa);

// agrego el pin al mapa al elegir una dirección
function ubicar(coordenadas) {
    // borro los marcadores anteriores
    mapa.eachLayer((layer) => {
        if (layer instanceof L.Marker) { layer.remove(); }
    });

    mapa.setView(coordenadas, 17)
    let pin = L.marker(coordenadas, { icon: icono_pin }).addTo(mapa);
}
