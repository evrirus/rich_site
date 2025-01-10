const WorkButton = $('#main-circuit');

// Переменные для буферизации кликов
let clickBuffer = 0; // Количество кликов, накопленных в буфере
let isSyncing = false; // Флаг синхронизации с сервером
let clickThreshold = 7;
let disabled = false;

// Обработчик клика
WorkButton.on('click', function () {
    // Если кнопка не заблокирована
    if (!disabled) {
        clickBuffer++; // Увеличиваем счетчик кликов
        console.log(`Клики в буфере: ${clickBuffer}`);
    }

    // Если кнопка еще не заблокирована, заблокировать ее на 3 секунды
    if (!disabled) {
        disabled = true; // Устанавливаем флаг заблокированного состояния
        WorkButton.addClass('disabled');  // Добавляем класс для блокировки кнопки

        // Убираем блокировку через 3 секунды
        setTimeout(function () {
            WorkButton.removeClass('disabled');  // Убираем класс
            disabled = false;  // Сбрасываем флаг
        }, 300);  // 3000 миллисекунд = 3 секунды
    }

    // Если количество кликов в буфере достигло порога, синхронизируем с сервером
    if (clickBuffer === clickThreshold) {
        syncWithServer();
    }

    // Если происходит синхронизация, сбрасываем счетчик кликов
    if (isSyncing) {
        clickBuffer = 0;
    }
});

window.addEventListener('beforeunload', function (event) {

    syncWithServer();
    event.preventDefault();
    event.returnValue = "";
});

function processServerData(data) {
    console.log(data);
    $('#earned-value .value').text(data.total_earnings.toLocaleString('ru-RU'));
    $('#level-value .value').text(data.current_level);

    $('#balance-value .value').text(data.current_balance.toLocaleString('ru-RU'));

    $('#salary-value .value').text(data.salary.toLocaleString('ru-RU'));
    $('#sphere-value .value').text(data.job.sphere.toLocaleString('ru-RU'));
    $('#job-value .value').text(data.job.name.toLocaleString('ru-RU'));

    $('#progress')
        .attr('max', data.required_exp)
        .attr('value', data.current_exp);
}

// Функция для отправки данных на сервер
function syncWithServer() {
    if (clickBuffer === 0 || isSyncing) return; // Нечего отправлять или уже идет синхронизация

    isSyncing = true; // Устанавливаем флаг синхронизации
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    $.ajax({
        url: '/api/update_clicks/', // URL эндпоинта на сервере
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        data: JSON.stringify({ clicks: clickBuffer }),
        contentType: 'application/json',
        success: function (response) {

            clickBuffer = 0; // Очищаем буфер после успешной отправки
            isSyncing = false; // Снимаем флаг синхронизации
            console.log(response)
            processServerData(response);
        },
        error: function (error) {

            handleMessages(error.responseJSON.error);

            isSyncing = false; // Снимаем флаг синхронизации даже при ошибке
        },
    });
}

// Автоматическая синхронизация каждые 10 секунд
setInterval(syncWithServer, 5000);


