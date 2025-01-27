$('#loginForm').on('submit', function (event) {
    event.preventDefault();

    const formData = $(this);
    console.log(LOGIN_URL)
    $.ajax({
        url: LOGIN_URL,
        type: "POST",
        data: formData.serialize(),
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (response) {
            console.log(response);
            if (response.success) {
                handleNotifications('Вход успешен!', 'success');
                window.location.href = PROFILE_URL;

            } else {
                handleNotifications(response.errors);
            }
        },
        error: function (error) {
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

