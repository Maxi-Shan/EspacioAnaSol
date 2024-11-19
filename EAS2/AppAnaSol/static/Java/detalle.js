// Función para obtener los parámetros de la URL
function obtenerParametrosDeURL() {
    const params = new URLSearchParams(window.location.search);
    const dia = params.get('dia');
    const mes = params.get('mes');
    const anio = params.get('anio');
    const hora = params.get('hora');
    return { dia, mes, anio, hora };
}

// Obtener los datos de la URL y mostrar la fecha y la hora seleccionadas
const { dia, mes, anio, hora } = obtenerParametrosDeURL();

const fechaReservaElem = document.getElementById('fecha-reserva');
const horaReservaElem = document.getElementById('hora-reserva');
const valorReservaElem = document.getElementById('valor-reserva');

// Mostrar la fecha y hora en el HTML
fechaReservaElem.textContent = `${dia}/${mes}/${anio}`;
horaReservaElem.textContent = hora;
valorReservaElem.textContent = '$' + valorReserva.toFixed(2); // Suponiendo que `valorReserva` está definido

// Manejar el envío del formulario
document.getElementById('formulario-reserva').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevenimos el envío del formulario

    const nombre = document.getElementById('nombre').value;
    const celular = document.getElementById('celular').value;
    const comprobante = document.getElementById('comprobante').files[0];

    if (nombre && celular && comprobante) {
        // Aquí puedes enviar los datos al backend (AJAX o Fetch API)
        alert(`Turno reservado para ${nombre}. Fecha: ${fechaReservaElem.textContent}, Hora: ${horaReservaElem.textContent}, Valor de reserva: $${valorReserva.toFixed(2)}`);

        // Ocultar el modal después de la confirmación (si tienes un modal)
        if (modalConfirmacion) {
            modalConfirmacion.style.display = 'none';
        }

        // Limpiar el formulario
        document.getElementById('formulario-reserva').reset();
    } else {
        alert("Por favor, completa todos los campos y sube el comprobante.");
    }
});
