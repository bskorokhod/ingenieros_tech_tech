// Estructura basada en la dada por Boostrap para validar formularios
(() => {
    'use strict';

    const formulario = document.getElementById('formulario-login');

    formulario.addEventListener("submit", event => {
        if (!formulario.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        formulario.classList.add('was-validated');
    })
})()