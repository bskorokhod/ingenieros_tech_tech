/**
 * Obtiene totalidad de datos de API de normalizacion de direcciones AMBA para toda direccion que se asemeje a la ingresada por el usuario
 */
function obtener_datos_API_normalizacion(){
    
    const url = `http://servicios.usig.buenosaires.gob.ar/normalizar?direccion=${input_usuario.value}&geocodificar=TRUE`
    const modalError = new bootstrap.Modal(document.getElementById('popUpError'))
    
    fetch(url)
    .then(respuesta => {
        if(!respuesta.ok){
            modalError.show()
            return
        }
        return respuesta.text(); }
    ).then(datos => {
        let obj_datos = JSON.parse(datos); 
        mostrar_direcciones_obtenidas(obj_datos['direccionesNormalizadas']);
    })
}


/**
 * Muestra las direcciones obtenidas por la API de normalización
 * @param {array} datos array de objetos obtenidos de la API de normalización
 */
function mostrar_direcciones_obtenidas(datos){
    
    // muestra solo las direcciones que tengan una coordenada asociada   
    const datos_filtrados = datos.filter((elem)=> 'coordenadas' in elem)

    if(datos_filtrados.length == 0){
        let parrafo = document.createElement('p');
        let textoParrafo = document.createTextNode('No se encontraron coincidencias :(')
        
        parrafo.appendChild(textoParrafo)
        parrafo.classList.add('mb-1')   
        div_resultados_busqueda.appendChild(parrafo);
    }


    for(const dato of datos_filtrados){
       
        let parrafo = document.createElement('p');
        let textoParrafo = document.createTextNode(dato.direccion)
        let span = document.createElement('span')
        let textoSpan = document.createTextNode(` (Localidad: ${dato.nombre_localidad})`)
        
        span.classList.add("fw-light", "opacity-75")
        span.appendChild(textoSpan)
        
        parrafo.setAttribute('coord_x', dato.coordenadas.x)
        parrafo.setAttribute('coord_y', dato.coordenadas.y)
        
        parrafo.appendChild(textoParrafo)
        parrafo.appendChild(span)
        
        
        parrafo.classList.add('mb-1')               
        div_resultados_busqueda.appendChild(parrafo);
    

        parrafo.addEventListener('click', function(elem){
            obtener_coordenadas_opcion_elegida(elem.currentTarget)
            div_busqueda.classList.add('d-none')
        })

    }
    spinner.classList.add('d-none')
    
}


/**
 * A partir de una opcion de direccion elegida, obtiene su nombre, coordenada x y coordenada y 
 */
function obtener_coordenadas_opcion_elegida(opcion){
    console.log(opcion)
    let coordX = opcion.getAttribute('coord_x')
    let coordY = opcion.getAttribute('coord_y')
    let direccion = opcion.textContent

    form_coord_x.value = coordX
    form_coord_y.value = coordY
    form_direccion.value = direccion
    input_usuario.value = direccion
}


// INPUT INICIAL
const input_usuario = document.getElementById('inputDireccion')

// ELEMENTOS HTML UTILIZADOS EN LA BUSQUEDA
const div_busqueda = document.getElementById('divBusqueda');
const div_resultados_busqueda = document.getElementById('resultados');
const spinner = document.getElementById('spinner')


// INPUTS OCULTOS QUE TOMA EL BACK
const form_coord_x = document.getElementById('coordX')
const form_coord_y = document.getElementById('coordY')
const form_direccion = document.getElementById('direccion')


input_usuario.addEventListener('change', function(){
    div_busqueda.classList.remove('d-none')
    div_resultados_busqueda.innerHTML = ''
  
    form_coord_x.value = ''
    form_coord_y.value = ''
    form_direccion.value = ''

    spinner.classList.remove('d-none')
    obtener_datos_API_normalizacion()
})



