$(function () {
    "use strict";

    const items = [
        "🍭", "🦄", "💵", "🦖", "👻"
    ];
    const $form = $('#userForm');
    const $mainButton = $('#submit_bid');
    const $buttonx05 = $('#bid__x05');
    const $buttonx2 = $('#bid__x2');
    const $buttonVaBank = $('#bid__vabank');
    const $freeSpin = $('#bid__freespin');
    const $inputBid = $('#input__bid');
    const $selectType = $('#choose_type_cash');
    const buttonsIsDisabled = false;

    const $doors = $(".door");
    let isSpinning = false;

    $form.on('submit', function (event) {
        event.preventDefault(); // Предотвращаем отправку формы по умолчанию

        const bidValue = $inputBid.val().trim(); // Убираем лишние пробелы

        // Проверяем, является ли значение числом
        if (isNaN(bidValue) || bidValue === '' || parseFloat(bidValue) < 150) {
            return handleMessages('Введите корректное число, больше или равное 150');
        }


        const submitter = event.originalEvent.submitter; // Получаем DOM-элемент кнопки
        let bid = $inputBid.val();

        if ($(submitter).is($buttonx05)) {
            bid = setBidValue(Math.floor(bid / 2));

        } else if ($(submitter).is($buttonx2)) {
            bid = setBidValue(Math.floor(bid * 2));

        } else if ($(submitter).is($buttonVaBank)) {
            // Когда нажата кнопка "ВАБАНК", отправляем 'vabank', но инпут не меняется
            bid = setBidValue(bid, 'vabank');

        } else if ($(submitter).is($freeSpin)) {
            bid = setBidValue(bid, 'freespin');

        } else if ($(submitter).is($mainButton)){
            null;

        } else {
            return
        }


        if (buttonsIsDisabled) {
            return
        } else {
            toggleButtonState(true)
            setTimeout(function() {
                toggleButtonState(false)
            }, 1900);
        }


        if (isSpinning) return; // Предотвращаем запуск нескольких спинов одновременно
        isSpinning = true;

        const formData = $form.serializeArray();
        formData.push({ name: 'bid', value: bid });

        // Запрос комбинации с сервера
        fetchCombinationFromServer(formData).then(data => {

            if (!data) {
                isSpinning = false;
                return;
            }
            console.log(data);
            let combination = data.combination;
            let message = data.notify;
            let winnings = data.winnings;
            let balance = data.balance;
            let choice = data.user_choice;

            // Инициализация перед запуском
            init(false);

            const duration = parseFloat(getComputedStyle($doors[0].querySelector(".boxes")).transitionDuration) * 1000;
            const delay = 400; // Задержка между началом анимации барабанов (в миллисекундах)

            // Запуск анимации всех барабанов с задержкой
            $doors.each(function (index, door) {
                setTimeout(() => {
                    const $boxes = $(door).find(".boxes");
                    $boxes.css({
                        transition: "transform 1s ease-out",
                        transform: `translateY(-${$(door).height() * ($boxes.children().length - 1)}px)`
                    });
                }, index * delay);
            });

            // Ожидание завершения всех анимаций
            setTimeout(() => {
                // Отображение комбинации на экране
                $doors.each(function (index, door) {
                    const $boxes = $(door).find(".boxes");
                    const $box = $("<div>", {
                        class: "box",
                        text: combination[index]
                    }).css({
                        width: $(door).width() + "px",
                        height: $(door).height() + "px"
                    });
                    $boxes.append($box);
                    $boxes.css({
                        transform: `translateY(-${$(door).height() * ($boxes.children().length - 1)}px)`
                    });
                });

                isSpinning = false;
            }, duration + delay * ($doors.length - 1));

            setTimeout(() => {
                handleMessages(message);
                addNotification($selectType.val(), winnings);
                updateBalance(choice, balance);
            }, 1900)

        });
    });

    function updateBalance(choice, amount) {
        const $amountBalance = $(`#text_amount_${choice}`)
        $amountBalance.html(amount.toLocaleString('ru-RU'));
    }

    function addNotification(currency, amount) {
        // Найдем элемент уведомления по валюте
        const $notificationElement = $(`#amount_${currency} .balance_notification`);

        // Установим текст уведомления (например, " +140 " или любой другой текст)
        console.log(amount, amount.toString()[0]);

        // Преобразуем amount в строку, если это не строка
        const amountStr = amount.toString();

        if (amountStr[0] === '-') {
            $notificationElement.text(`${amountStr} ${currency === 'cash' ? '₽' : (currency === 'dollar' ? '$' : '₿')}`);
            $notificationElement.addClass('failed');
        } else {
            $notificationElement.text(`+${amountStr} ${currency === 'cash' ? '₽' : (currency === 'dollar' ? '$' : '₿')}`);
            $notificationElement.addClass('winned');
        }

        // Покажем уведомление
        $notificationElement.addClass('show');

        // Скрыть уведомление через 3 секунды (3000 миллисекунд)
        setTimeout(() => {
            $notificationElement.removeClass('show');
            setTimeout(() => {
                $notificationElement.removeClass('failed');
                $notificationElement.removeClass('winned');
            }, 190);
        }, 1800);
    }

    function toggleButtonState(state) {
        $mainButton.prop("disabled", state);
        $buttonx05.prop("disabled", state);
        $buttonx2.prop("disabled", state);
        $buttonVaBank.prop("disabled", state);
        $freeSpin.prop("disabled", state);
    }

    function setBidValue(value, type=null) {

        if (type === 'vabank') {
            return type;
        }
        if (type === 'freespin') {
            return type
        }

        $('#input__bid').val(value);
        return value;

    }

    function fetchCombinationFromServer(formData) {

        return $.ajax({
            url: '/api/slot/generate/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            data: formData,
            dataType: 'json'
        }).then(response => {

            if (response.combination && response.notify) {
                return response;
            } else {
                return null;
            }
        }).catch(() => console.log('Возникла неизвестная ошибка'));
    }

    function init(firstInit = true) {
        $doors.each(function () {
            const $door = $(this);
            const $boxes = $door.find(".boxes");
            const $boxesClone = $("<div>", { class: "boxes" });
            $(".info").html(`<span class="smile">${items.join("</span> <span class=\"smile\">")}</span>`);

            let pool = [];

            if (firstInit) {
                // Изначально отображаем только вопросительные знаки
                for (let i = 0; i < 20; i++) {
                    pool.push("❓");
                }
            } else {
                // Заполняем случайными символами
                for (let i = 0; i < 20; i++) {
                    pool.push(...items);
                }
                // Перемешиваем элементы
                pool = shuffle(pool);
            }

            // Перемешиваем элементы
            const shuffledItems = shuffle(pool);

            shuffledItems.forEach(item => {
                const $box = $("<div>", {
                    class: "box",
                    text: item
                }).css({
                    width: $door.width() + "px",
                    height: $door.height() + "px"
                });
                $boxesClone.append($box);
            });

            $boxesClone.css({
                transition: "none",
                transform: `translateY(0px)`
            });
            $door.find(".boxes").replaceWith($boxesClone);
        });
    }

    function shuffle(arr) {
        let m = arr.length;
        while (m) {
            const i = Math.floor(Math.random() * m--);
            [arr[m], arr[i]] = [arr[i], arr[m]];
        }
        return arr;
    }

    // Инициализация начального состояния
    init();
});
