document.addEventListener('DOMContentLoaded', function () {
    const dateInput = document.querySelector('.datepicker');

    if (dateInput) {
        dateInput.addEventListener('input', function () {
            if (this.value) { // Verificar que el usuario haya seleccionado una fecha
                const selectedDate = new Date(this.value + 'T00:00:00'); // Asegurar que se tome como fecha local
                
                // Si es domingo (0 = Domingo)
                if (selectedDate.getDay() === 0) {
                    alert("El local no atiende los domingos. Por favor, selecciona otra fecha.");
                    this.value = ''; // Limpiar la fecha seleccionada
                }
            }
        });
    }
});
