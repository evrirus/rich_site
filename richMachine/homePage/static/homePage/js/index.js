document.addEventListener('DOMContentLoaded', () => {

    const startButton = document.querySelector('.start_button');

    startButton.addEventListener('click', () => {
        window.location.href = '/profile';
    });

});