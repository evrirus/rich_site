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

    const $doors = $(".door");
    let isSpinning = false;

    $form.on('submit', function (event) {

        const submitter = event.originalEvent.submitter; // Получаем DOM-элемент кнопки
        let bid = $inputBid.val();
        console.log(bid);

        if ($(submitter).is($buttonx05)) {
            bid = setBidValue(Math.floor(bid / 2));

        } else if ($(submitter).is($buttonx2)) {
            bid = setBidValue(Math.floor(bid * 2));

        } else if ($(submitter).is($buttonVaBank)) {
            // Когда нажата кнопка "ВАБАНК", отправляем 'vabank', но инпут не меняется
            bid = setBidValue(bid, 'vabank');

        } else if ($(submitter).is($freeSpin)) {
            bid = setBidValue(bid, 'freespin');
        } else {
            console.log('Вы нажали на неизвестную кнопку');
        }


        event.preventDefault(); // Предотвращаем отправку формы по умолчанию

        if (isSpinning) return; // Предотвращаем запуск нескольких спинов одновременно
        isSpinning = true;

        const formData = $form.serializeArray();

        formData.push({ name: 'bid', value: bid });
        console.log(formData);

        // Запрос комбинации с сервера
        fetchCombinationFromServer(formData).then(combination => {
            if (!combination) {
                isSpinning = false;
                return;
            }

            // Инициализация перед запуском
            init(false);

            const duration = parseFloat(getComputedStyle($doors[0].querySelector(".boxes")).transitionDuration) * 1000;
            const delay = 200; // Задержка между началом анимации барабанов (в миллисекундах)

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
        });
    });

    function setBidValue(value, type=null) {
        console.log(value, type);

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
            console.log(response);
            if (response.combination) {
                return response.combination;
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
