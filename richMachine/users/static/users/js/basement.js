$(document).ready(function() {

    function formatNumberWithSpaces(number) {
        return number.toLocaleString('ru-RU'); // Используем локаль 'ru-RU' для формата с пробелами
    }

    function handleMessages(messages) {
        const container = $('#messages-container');
        messages.forEach(function(message) {
            const parts = message.message.split('|');
            const alertClass = 'alert-' + message.level;
            let alert = $('<div class="alert ' + alertClass + '"></div>');

            if (parts.length > 1) {
                alert.append('<strong>' + parts[0] + '</strong><br>' + parts[1]);
            } else {
                alert.text(message.message);
            }

            // Добавляем уведомление в начало контейнера
            container.prepend(alert);

            // Удаляем уведомление через 5 секунд
            setTimeout(() => {
                alert.fadeOut(500, function() {
                    $(this).remove();
                });
            }, 5000);
        });
    }

    const takeProfitButton = $('#take-profit');
    takeProfitButton.on('click', function(event) {

        const houseId = takeProfitButton.attr('house-id');
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        $.ajax({
            type: 'POST',
            url: "/api/take_profit_basement/",
            data: houseId,
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            success: function(response) {
                console.log(response);
                if (response.success) {
                    $('#current-balance').text(response.new_balance);
                }
                handleMessages(response.messages);
            },
            error: function(xhr, status, error) {
                alert('Произошла ошибка: ' + error);
            }
        });
    });

    const createBasement = $('#create-basement__button');
    createBasement.on('click', function (event) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const houseId = createBasement.attr('house-id');

        $.ajax({
            type: 'POST',
            url: "/api/create_basement/",
            data: houseId,
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            success: function(response) {
                console.log(response);
                if (response.success) {

                    $('.empty').text('Ваш подвал пуст!');
                    $('#create-basement').remove();
                    $('#limit-videocards').text(10);
                }
                handleMessages(response.messages);
                // setTimeout(function(){ location.reload()},3000);

            },
            error: function(xhr, status, error) {
                alert('Произошла ошибка: ' + error);
            }
        });

    })

    const upgradeBasement = $('#upgrade-basement__button');
    upgradeBasement.on('click', function (event) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const houseId = upgradeBasement.attr('house-id');

        $.ajax({
            type: 'GET',
            url: `/api/upgrade_basement/${houseId}/`,
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            success: function(response) {
                console.log(response);
                if (response.success) {

                    $('.empty').text('Ваш подвал пуст!');
                    // $('#upgrade-basement').remove();
                    $('#limit-videocards').text();
                }
                handleMessages(response.messages);
                // setTimeout(function(){ location.reload()},3000);

            },
            error: function(xhr, status, error) {
                alert('Произошла ошибка: ' + error);
            }
        });

    });
});
  
  