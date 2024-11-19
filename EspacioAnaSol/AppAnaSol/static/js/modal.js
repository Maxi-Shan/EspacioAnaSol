document.addEventListener('DOMContentLoaded', function() {
    // Obtener todas las imágenes de los comprobantes y diseños de uñas
    const imagenesComprobante = document.querySelectorAll('.comprobante-img');
    const imagenesDiseño = document.querySelectorAll('.diseño-img');

    // Crear el modal
    const modal = document.createElement('div');
    modal.classList.add('modal');
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-btn">&times;</span>
            <img class="modal-img" src="" alt="Imagen del Turno" />
        </div>
    `;
    document.body.appendChild(modal);

    // Función para abrir el modal
    function abrirModal(imagenSrc) {
        const modalImg = modal.querySelector('.modal-img');
        modalImg.src = imagenSrc;
        modal.style.display = 'block';
    }

    // Función para cerrar el modal
    function cerrarModal() {
        modal.style.display = 'none';
    }

    // Añadir el evento de clic en cada imagen de comprobante
    imagenesComprobante.forEach(imagen => {
        imagen.addEventListener('click', function() {
            abrirModal(imagen.src);
        });
    });

    // Añadir el evento de clic en cada imagen de diseño de uñas
    imagenesDiseño.forEach(imagen => {
        imagen.addEventListener('click', function() {
            abrirModal(imagen.src);
        });
    });

    // Evento para cerrar el modal cuando se haga clic en el botón de cierre
    const closeBtn = modal.querySelector('.close-btn');
    closeBtn.addEventListener('click', cerrarModal);

    // Cerrar el modal si se hace clic fuera de la imagen
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            cerrarModal();
        }
    });
});
