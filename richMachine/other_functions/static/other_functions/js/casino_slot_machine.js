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

// Функция для получения CSRF токена из cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

(async function () {
    "use strict";

    const items = [
        "🍭", "🦄", "💵", "🦖", "👻"
    ];
    const form = document.getElementById('userForm');
    const doors = document.querySelectorAll(".door");
    let isSpinning = false;

    document.getElementById('userForm').addEventListener('submit', async function (event) {
        event.preventDefault(); // Предотвращаем отправку формы по умолчанию

        if (isSpinning) return; // Предотвращаем запуск нескольких спинов одновременно
        isSpinning = true;

        const formData = new FormData(form);

        // Запрос комбинации с сервера
        const combination = await fetchCombinationFromServer(formData);
        if (!combination) {
            isSpinning = false;
            return;
        }

        // Инициализация перед запуском
        init(false);

        const duration = parseFloat(getComputedStyle(doors[0].querySelector(".boxes")).transitionDuration) * 1000;
        const delay = 200; // Задержка между началом анимации барабанов (в миллисекундах)

        // Запуск анимации всех барабанов с задержкой
        doors.forEach((door, index) => {
            setTimeout(() => {
                const boxes = door.querySelector(".boxes");
                boxes.style.transition = "transform 1s ease-out";
                boxes.style.transform = `translateY(-${door.clientHeight * (boxes.childElementCount - 1)}px)`;
            }, index * delay);
        });

        // Ожидание завершения всех анимаций
        await new Promise(resolve => setTimeout(resolve, duration + delay * (doors.length - 1)));

        // Отображение комбинации на экране
        doors.forEach((door, index) => {
            const boxes = door.querySelector(".boxes");
            const box = document.createElement("div");
            box.classList.add("box");
            box.style.width = door.clientWidth + "px";
            box.style.height = door.clientHeight + "px";
            box.textContent = combination[index];
            boxes.appendChild(box);
            boxes.style.transform = `translateY(-${door.clientHeight * (boxes.childElementCount - 1)}px)`;
        });

        isSpinning = false;
    });

    async function fetchCombinationFromServer(formData) {
        try {
            const formDataObj = Object.fromEntries(formData.entries());
 
            const response = await fetch('generate_combination/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formDataObj)
            });

            const data = await response.json();

            if (data.combination) {
                handleMessages(data.messages)
                return data.combination;
            } else {
                handleMessages(data.messages)
                return null;
            }
        } catch (error) {
            return null;
        }
    }

    function init(firstInit = true) {
        doors.forEach(door => {
            const boxes = door.querySelector(".boxes");
            const boxesClone = document.createElement("div");
            boxesClone.className = "boxes";
            document.querySelector(".info").textContent = `${items.join(" ")}`;

            let pool = [];

            if (firstInit) {
                // Изначально отображаем только вопросительные знаки
                for (let i = 0; i < 20; i++) { // Убедитесь, что символов достаточно
                    pool.push("❓");
                }
            } else {
                // Заполняем случайными символами
                for (let i = 0; i < 20; i++) { // Убедитесь, что символов достаточно
                    pool.push(...items);
                }
                // Перемешиваем элементы
                pool = shuffle(pool);
            }

            // Перемешиваем элементы
            const shuffledItems = shuffle(pool);

            shuffledItems.forEach(item => {
                const box = document.createElement("div");
                box.classList.add("box");
                box.style.width = door.clientWidth + "px";
                box.style.height = door.clientHeight + "px";
                box.textContent = item;
                boxesClone.appendChild(box);
            });

            boxesClone.style.transition = "none"; // Отключаем анимацию при изменении
            boxesClone.style.transform = `translateY(0px)`;
            door.replaceChild(boxesClone, boxes);
        });
    }

    function getVisibleSymbol(door) {
        // Получение видимого символа
        const visibleBox = door.querySelector(".boxes .box:last-child");
        return visibleBox ? visibleBox.textContent : "❓";
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
})();
