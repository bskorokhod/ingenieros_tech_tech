const select_tipo_mascota = document.getElementById('tipoMascota')
const select_raza = document.getElementById('razaMascota')
const select_color = document.getElementById('colorPrincipalMascota')


const razas = Array.from(document.getElementById('razaMascota').getElementsByTagName('option'))
const razas_perros = razas.filter((elem)=> elem.dataset.tipoMascota == 'perro' )
const razas_gatos = razas.filter((elem)=> elem.dataset.tipoMascota == 'gato')

const colores = Array.from(document.getElementById('colorPrincipalMascota').getElementsByTagName('option'))
const colores_perros = colores.filter((elem)=> elem.dataset.tipoMascota == 'perro' )
const colores_gatos = colores.filter((elem)=> elem.dataset.tipoMascota == 'gato')


select_tipo_mascota.addEventListener('change', (event)=>{ editar_selects_por_tipo(event.target) })

function editar_selects_por_tipo(opcion){
    razas[0].selected = true
    colores[0].selected = true

    switch(opcion.value){
        case 'perro':{
            mostrar_esconder_opcs('mostrar', razas_perros, colores_perros)
            mostrar_esconder_opcs('esconder', razas_gatos, colores_gatos)
            select_raza.disabled = false
            select_color.disabled = false
            
            break
        }
        case 'gato':{
            mostrar_esconder_opcs('mostrar', razas_gatos, colores_gatos)
            mostrar_esconder_opcs('esconder', razas_perros, colores_perros)
            select_raza.disabled = false
            select_color.disabled = false

            break
        }
        default:{

            select_raza.disabled = true
            select_color.disabled = true

            break
        }
    }
}


function mostrar_esconder_opcs(accion, array_raza, array_color){
    if(accion == 'mostrar'){
        array_raza.forEach((elem)=> elem.classList.remove('d-none'))
        array_color.forEach((elem)=> elem.classList.remove('d-none'))
    }else{
        array_raza.forEach((elem)=> elem.classList.add('d-none'))
        array_color.forEach((elem)=> elem.classList.add('d-none'))
    }
}
