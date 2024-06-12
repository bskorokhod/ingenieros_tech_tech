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