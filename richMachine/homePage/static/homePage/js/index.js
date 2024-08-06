document.addEventListener('DOMContentLoaded', () => {

    const buttonFunctions = document.querySelector('.button-functions');
    const otherFunctions = document.querySelector('.other-functions');

    // Обработчик клика по кнопке
    buttonFunctions.addEventListener('click', (event) => {
        otherFunctions.style.display = 'flex';
        // Предотвращаем всплытие события клика на кнопку
        event.stopPropagation();
    });

    // Обработчик клика на документе
    document.addEventListener('click', (event) => {
        // Проверяем, был ли клик вне элемента otherFunctions и кнопки
        if (!otherFunctions.contains(event.target) && !buttonFunctions.contains(event.target)) {
            otherFunctions.style.display = 'none'; // Скрываем элемент
        }
    });
});