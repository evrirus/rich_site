document.addEventListener('DOMContentLoaded', () => {
    const houseItemsContainer = document.querySelector('.property'); 
    const modal = document.querySelector('#houseModal');
    const acceptBuyHouseButton = document.getElementById('accept_buy_house');
    const infoHouse = modal.querySelector('.info__house');

    const loadingIndicator = modal.querySelector('.loader');
    // Создаем объект кеша
    const cache = {};

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

    let currentHouseId = null;
    console.log(houseItemsContainer, modal);
    if (houseItemsContainer && modal) {
        houseItemsContainer.addEventListener('click', (event) => {
            const houseItem = event.target.closest('.house_item');
            if (houseItem) {
                openModal(event, houseItem);
            }
        });

        function openModal(event, item) {

            loadingIndicator.style.visibility = 'visible';
            infoHouse.style.visibility = 'hidden';
            modal.style.visibility = 'visible';
            
            const id = item.getAttribute('data-modal-id');
            const type = item.getAttribute('data-type');

            currentHouseId = id;
            const cacheKey = `${type}-${id}`;  // Ключ для кеша

            // Проверяем кеш
            if (cache[cacheKey]) {
                updateModalContent(cache[cacheKey]);
            } else {
                // Подгрузка данных из БД с использованием AJAX
                $.ajax({
                    type: 'GET',
                    url: `../get_house_info/${id}/`,  // URL вашего API эндпоинта
                    success: function(response) {
                        // Сохраняем данные в кеш
                        cache[cacheKey] = response;
                        // Обновление содержимого модального окна
                        updateModalContent(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Ошибка при загрузке данных: ', error);
                    }
                });
            }
            modal.style.left = `${event.layerX}px`; 
            modal.style.top = `${event.layerY}px`; 
            
        }

        function updateModalContent(data) {

            document.querySelector('.house-district-name').textContent = `${data.district_name}`;
            document.querySelector('.house-type').textContent = `${data.house_type} №`;
            document.querySelector('#house_id_district').textContent = `${data.house_id_for_district}`;

            document.querySelector('#house_id').textContent = `${data.house_id}`;
            document.querySelector('#house_price').textContent = `${data.house_price} ₽`;
            document.querySelector('#house_basement').innerHTML = `${data.house_basement}`;
            document.querySelector('#house_floors').textContent = `${data.house_floor}`;
            document.querySelector('#house_class').textContent = `${data.house_class}`;
            
            loadingIndicator.style.visibility = 'hidden';
            infoHouse.style.visibility = 'visible';
            modal.style.visibility = 'visible';
        }

        function closeModal() {
            modal.style.visibility = 'hidden';
            infoHouse.style.visibility = 'hidden';
        }

        window.addEventListener('click', (event) => {
            if (!modal.contains(event.target) && !event.target.closest('.house_item')) {
                closeModal();
            }
        });

        // Добавляем обработчик для кнопки покупки
        if (acceptBuyHouseButton) {
            acceptBuyHouseButton.addEventListener('click', function() {
        
                loadingIndicator.style.visibility = 'visible'; // Показываем индикатор загрузки
        
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
                $.ajax({
                    url: '../buy_house/' + currentHouseId + '/',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    data: {
                        id: currentHouseId
                    },
                    success: function(data) {
                        loadingIndicator.style.visibility = 'hidden'; // Скрываем индикатор загрузки
                        handleMessages(data.messages);
                        closeModal();
                    },
                    error: function(error) {
                        loadingIndicator.style.visiblity = 'hidden'; // Скрываем индикатор загрузки
                        alert('Произошла ошибка: ' + error.responseJSON.message || 'Неизвестная ошибка');
                    }
                });
            });
        }
        
    } else {
        console.error('Один из элементов не найден: houseItemsContainer или modal');
    }
});
