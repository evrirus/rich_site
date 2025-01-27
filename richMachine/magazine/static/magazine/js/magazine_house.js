document.addEventListener('DOMContentLoaded', () => {
    const houseItemsContainer = document.querySelector('.property'); 
    const modal = document.querySelector('#houseModal');
    const acceptBuyHouseButton = document.getElementById('accept_buy_house');
    const infoHouse = modal.querySelector('.info__house');

    const loadingIndicator = modal.querySelector('.loader');
    // Создаем объект кеша
    const cache = {};

    let currentHouseId = null;
    
    function formatNumberWithSpaces(number) {
        return number.toLocaleString('ru-RU'); // Используем локаль 'ru-RU' для формата с пробелами
    }

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
                    url: `/api/get_house/${id}/`,  // URL вашего API эндпоинта
                    success: function(response) {
                        // Сохраняем данные в кеш
                        cache[cacheKey] = response;
                        console.log(response);
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
            
            let basement_text;
            if (data.basement > 0) {
                basement_text = `Имеется[<span style='color: rgb(255, 28, 28);'>lvl</span>=${data.basement}]`;
            } else {
                basement_text = 'Отсутствует';
            }

            document.querySelector('.house-district-name').textContent = `${data.district_info.name}`;
            document.querySelector('.house-type').textContent = `${data.type} №`;
            document.querySelector('#house_id_district').textContent = `${data.id_for_district}`;

            document.querySelector('#house_id').textContent = `${data.id}`;
            document.querySelector('#house_price').textContent = `${formatNumberWithSpaces(data.price)} ₽`;
            document.querySelector('#house_basement').innerHTML = `${basement_text}`;
            document.querySelector('#house_floors').textContent = `${data.floors}`;
            document.querySelector('#house_class').textContent = `${data.class}`;
            
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
                    url: '/api/buy_house/',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    data: {
                        id: currentHouseId
                    },
                    success: function(data) {
                        loadingIndicator.style.visibility = 'hidden'; // Скрываем индикатор загрузки
                        closeModal();
                    },
                    error: function(error) {
                        console.log(error)
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
