document.addEventListener('DOMContentLoaded', () => {


    const logoutButton = document.getElementById('logout-button')
    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            event.preventDefault(); // Отменяем переход по ссылке

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/users/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Если используется CSRF защита, добавьте токен
                },
            })
            .then(response => {
                if (response.ok) {
                    // Успешный выход, можно перенаправить пользователя или обновить интерфейс
                    window.location.href = '/users/login/'; // Перенаправление на главную страницу или другую
                } else {
                    // Обработка ошибок
                    console.error('Ошибка при выходе:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Ошибка сети:', error);
            });
        })}
    });