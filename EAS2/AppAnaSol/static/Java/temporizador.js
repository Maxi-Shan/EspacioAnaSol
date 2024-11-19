let timerElement = document.getElementById("timer");
        let timeRemaining = 60; // 

        function startTimer() {
            let countdown = setInterval(function () {
                let minutes = Math.floor(timeRemaining / 60);
                let seconds = timeRemaining % 60;

                // Mostrar el tiempo en formato MM:SS
                timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

                timeRemaining--;

                // Redirigir al cliente si el tiempo se agota
                if (timeRemaining < 0) {
                    clearInterval(countdown);
                    window.location.href = tiempoAgotadoUrl;
                }
            }, 1000);
        }

        // Iniciar el temporizador al cargar la página
        window.onload = startTimer;