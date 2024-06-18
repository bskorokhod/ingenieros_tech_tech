// creo los íconos
const icono_pin = L.icon({ iconUrl: '../static/icons/pin.svg', iconSize: [30, 30] });
const pata_perro = L.icon({ iconUrl: '../static/icons/pata_perro.svg', iconSize: [50, 50] });
const pata_gato = L.icon({ iconUrl: '../static/icons/pata_gato.svg', iconSize: [30, 30] });
const icono_refugio = L.icon({ iconUrl: '../static/icons/refugio.svg', iconSize: [30, 30] });


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
    mapa.eachLayer((layer) => { if (layer instanceof L.Marker) { layer.remove(); } });

    // muevo el mapa a las coordenadas elegidas y agrego el marcador
    mapa.setView(coordenadas, 17);
    let pin = L.marker(coordenadas, { icon: icono_pin }).addTo(mapa);
}


// agrego el marcador al mapa por cada mascota
function mostrar_mascotas(mascotas) {
    for (let mascota of mascotas) {
        let latitud = mascota.dataset.coordy;
        let longitud = mascota.dataset.coordx;
        let coordenadas = [latitud, longitud];
        
        // agrego una pata de perro o de gato según corresponda
        if (mascota.dataset.animal == 'perro') {
            let marcador = L.marker(coordenadas, { icon: pata_perro }).addTo(mapa);
            marcador.bindPopup(mascota.dataset.nombre, { closeButton: false, className: 'popup_mascota' });
        } else {
            let marcador = L.marker(coordenadas, { icon: pata_gato }).addTo(mapa);
            marcador.bindPopup(mascota.dataset.nombre, { closeButton: false, className: 'popup_mascota' });
        }
    }
}


// agrego el marcador al mapa por cada refugio
function mostrar_refugios(refugios) {
    for (let refugio of refugios) {
        let latitud = refugio.dataset.coordy;
        let longitud = refugio.dataset.coordx;
        let coordenadas = [latitud, longitud];
        
        let marcador = L.marker(coordenadas, { icon: icono_refugio }).addTo(mapa);
        marcador.bindPopup(refugio.dataset.nombre, { closeButton: false, className: 'popup_refugio' });
    }
}


// agrego el marcador al mapa por cada mascota
const tarjetas_mascotas = document.querySelectorAll('.tarjeta-mascota');
mostrar_mascotas(tarjetas_mascotas);


// agrego el marcador al mapa por cada refugio
const tarjetas_refugios = document.querySelectorAll('.tarjeta-refugio');
mostrar_refugios(tarjetas_refugios);
