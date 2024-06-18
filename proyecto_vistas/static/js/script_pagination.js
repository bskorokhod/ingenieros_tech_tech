const btn_siguiente = document.getElementById('siguiente')
const btn_anterior = document.getElementById('anterior')
const pag_actual = document.getElementById('pagActual')

const filtros = document.getElementById('formFiltros')
const selects_form = document.getElementsByTagName('select')

const input_pag_form = document.getElementById('inputPagActual')

btn_siguiente.addEventListener('click', () => {
    input_pag_form.value = parseInt(input_pag_form.value) + 1
    filtros.submit()
})

btn_anterior.addEventListener('click', () => {
    input_pag_form.value = parseInt(input_pag_form.value) - 1
    filtros.submit()
})

Array.from(selects_form).forEach((elem) => {
    elem.addEventListener('change', () => {
        input_pag_form.value = 1
    })
})