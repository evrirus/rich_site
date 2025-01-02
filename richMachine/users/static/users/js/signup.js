$('#registrationForm').on('submit', function (event) {
    event.preventDefault();

    if (!telegramAuthenticated) {
        handleNotifications('Пожалуйста, выполните вход через Telegram.', 'error');
        return;
    }

    const username = $('#id_username').val();
    const password1 = $('#id_password1').val();
    const password2 = $('#id_password2').val();

    if (username.length < 3 || username.length > 20) {
        handleNotifications('Имя пользователя должно быть от 3 до 20 символов.', 'error');
        return;
    }

    if (password1 !== password2) {
        handleNotifications('Пароли не совпадают.', 'error');
        return;
    }

    if (password1.length < 8) {
        handleNotifications('Пароль должен быть не менее 8 символов.', 'error');
        return;
    }

    // Если проверки пройдены, отправляем форму
    const formData = $(this).serialize();
    console.log(formData);
    console.log(REGISTER_URL);

    $.ajax({
        url: REGISTER_URL,
        type: "POST",
        data: formData,
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (response) {
            console.log(response);
            if (response.success) {

                handleNotifications('Регистрация успешна!', 'success');
                console.log(PROFILE_URL)
                // window.location.href = PROFILE_URL;

            } else {
                handleNotifications(response.errors);
            }
        },
        error: function (error) {
            console.log(error);
            const errors = error.errors || ["Ошибка отправки данных на сервер."];
            displayErrors(errors);
        }
    });

    function displayErrors(errors) {
        const container = $('#messages-container'); // Убедитесь, что контейнер существует в HTML
        container.empty(); // Очищаем предыдущие сообщения

        errors.forEach(error => {
            let alert = $('<div class="alert alert-danger"></div>').text(error);
            container.append(alert);
        });

        // Автоматическое скрытие сообщений
        setTimeout(() => {
            container.find('.alert').fadeOut(500, function () {
                $(this).remove();
            });
        }, 5000);
    }


    function handleNotifications(message, type = 'success') {
        const container = $('#messages-container');
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';

        let alert = $('<div class="alert ' + alertClass + '"></div>').text(message);
        container.prepend(alert);

        setTimeout(() => {
            alert.fadeOut(500, function () {
                $(this).remove();
            });
        }, 5000);
    }


});