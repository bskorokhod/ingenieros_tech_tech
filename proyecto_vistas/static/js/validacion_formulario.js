// Estructura basada en la dada por Boostrap para validar formularios
(() => {
  'use strict'

  const formulario = document.getElementById("formulario")
  const direccion = document.getElementById("form-direccion")

  formulario.addEventListener("submit", event => {
    if( !formulario.checkValidity() || !direccion_valida()){
        event.preventDefault()
        event.stopPropagation()
    }

    formulario.classList.add('was-validated')
    direccion.classList.add('was-validated')
  })

})()


function direccion_valida(){
  return document.getElementById('coordx').value != "" && document.getElementById('coordy') != ""
}

// VALIDACIÓN DE LA FECHA

document.getElementById('formulario').addEventListener('submit', event => {
  const fechaExtravio = document.getElementById('inputFechaExtravio').value;
  const fechaExtravio1 = new Date(fechaExtravio);
  const hoy = new Date();
  hoy.setHours(0,0,0,0);

  //comparo la fecha actual con la que ingresó el usuario
  if (fechaExtravio1 > hoy) {
    
    //muestro el modal
    const modalfecha = new bootstrap.Modal(document.getElementById('popUpErrorFecha'));
      
    modalfecha.show();

    }
});
