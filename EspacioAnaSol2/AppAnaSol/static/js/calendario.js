document.addEventListener('DOMContentLoaded', () => {
    let fechasOcupadas = JSON.parse('{{ fechas_ocupadas|safe|json_script:"fechas_ocupadas" }}');
    let mesActual = new Date().getMonth();
    let añoActual = new Date().getFullYear();
    const calendarContainer = document.getElementById('calendar');

    function getNombreMes(mes) {
        const nombresMeses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ];
        return nombresMeses[mes];
    }

    function cambiarMes(cambio) {
        mesActual += cambio;
        if (mesActual < 0) {
            mesActual = 11; 
            añoActual--;
        } else if (mesActual > 11) {
            mesActual = 0; 
            añoActual++;
        }
        generarCalendario();
    }

    function generarCalendario() {
        calendarContainer.innerHTML = '';
        
        const monthDiv = document.createElement('div');
        monthDiv.className = 'month';
        const monthTitle = document.createElement('h3');
        monthTitle.innerText = `${getNombreMes(mesActual)} ${añoActual}`;
        monthDiv.appendChild(monthTitle);
        
        const btnPrev = document.createElement('button');
        btnPrev.innerText = '<';
        btnPrev.onclick = () => cambiarMes(-1);
        monthDiv.appendChild(btnPrev);
        
        const btnNext = document.createElement('button');
        btnNext.innerText = '>';
        btnNext.onclick = () => cambiarMes(1);
        monthDiv.appendChild(btnNext);

        const diasEnMes = new Date(añoActual, mesActual + 1, 0).getDate();
        for (let dia = 1; dia <= diasEnMes; dia++) {
            const fechaCompleta = new Date(añoActual, mesActual, dia);
            const fechaString = fechaCompleta.toISOString().split('T')[0];

            const dayBtn = document.createElement('button');
            dayBtn.className = 'day';
            dayBtn.innerText = dia;

            if (fechasOcupadas.includes(fechaString)) {
                dayBtn.classList.add('ocupado');
                dayBtn.disabled = true;
            } else {
                dayBtn.onclick = () => seleccionarDia(fechaString);
            }

            monthDiv.appendChild(dayBtn);
        }

        calendarContainer.appendChild(monthDiv);
    }

    function seleccionarDia(fecha) {
        // Aquí puedes añadir la lógica para mostrar horas disponibles
        console.log("Día seleccionado:", fecha);
    }

    generarCalendario();
});
