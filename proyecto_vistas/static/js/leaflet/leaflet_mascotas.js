// creo los íconos de las patitas
const pata_perro = L.icon({
    iconUrl: '../static/icons/pata_perro.svg',
    iconSize: [50, 50]
});
const pata_gato = L.icon({
    iconUrl: '../static/icons/pata_gato.svg',
    iconSize: [30, 30]
});

// inicializo el mapa
let mapa = L.map('map', { attributionControl: false }).setView([-34.617777, -58.368758], 16);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    minZoom: 9,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(mapa);

// agrego el marcador al mapa por cada mascota
const tarjetas_mascotas = document.querySelectorAll('.tarjeta-mascota');
for (let mascota of tarjetas_mascotas) {
    let longitud = mascota.dataset.coordx;
    let latitud = mascota.dataset.coordy;
    let coordenadas = [latitud, longitud];

    if (mascota.dataset.animal == 'perro') {
        let marcador = L.marker(coordenadas, { icon: pata_perro }).addTo(mapa);
        marcador.bindPopup(mascota.dataset.nombre, { closeButton: false, className: 'popup_mascota' });
    } else {
        let marcador = L.marker(coordenadas, { icon: pata_gato }).addTo(mapa);
        marcador.bindPopup(mascota.dataset.nombre, { closeButton: false, className: 'popup_mascota' });
    }
}
