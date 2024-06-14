// creo el ícono del refugio
const icono_refugio = L.icon({
    iconUrl: '../static/icons/refugio.svg',
    iconSize: [30, 30]
});

// inicializo el mapa
let mapa = L.map('map', { attributionControl: false }).setView([-34.617777, -58.368758], 16);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    minZoom: 9,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(mapa);

// agrego el marcador al mapa por cada refugio
const tarjetas_refugios = document.querySelectorAll('.tarjeta-refugio');
for (let refugio of tarjetas_refugios) {
    let longitud = refugio.dataset.coordx;
    let latitud = refugio.dataset.coordy;
    let coordenadas = [longitud, latitud];

    let marcador = L.marker(coordenadas, { icon: icono_refugio }).addTo(mapa);
    marcador.bindPopup(refugio.dataset.nombre, { closeButton: false, className: 'popup_refugio' });
}
