document.addEventListener('DOMContentLoaded', () => {

    const buttonFunctions = document.querySelector('.button-functions');
    const otherFunctions = document.querySelector('.other-functions');

    // Обработчик клика на документе
    if (otherFunctions) {
        document.addEventListener('click', (event) => {
            otherFunctions.style.display = 'flex';
            // Предотвращаем всплытие события клика на кнопку
            event.stopPropagation();
            // Проверяем, был ли клик вне элемента otherFunctions и кнопки
            if (!otherFunctions.contains(event.target) && !buttonFunctions.contains(event.target)) {
                otherFunctions.style.display = 'none'; // Скрываем элемент
            }
        });
    }

    const logoutButton = document.getElementById('logout-button')
    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            event.preventDefault(); // Отменяем переход по ссылке

            const csrfToken = $('[name=csrfmiddlewaretoken]').val();

            fetch('/users/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Если используется CSRF защита, добавьте токен
                },
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/users/login/';

                } else {
                    console.error('Ошибка при выходе:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Ошибка сети:', error);
            });
        })}
    });