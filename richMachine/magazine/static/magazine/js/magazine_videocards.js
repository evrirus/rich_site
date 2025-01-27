document.addEventListener('DOMContentLoaded', () => {
    const videocardItemsContainer = document.querySelector('.property'); 
    const modal = document.querySelector('#videocardModal');
    const acceptBuyVideocardButton = document.getElementById('accept_buy_videocard');
    const infoCard = modal.querySelector('.info__videocard');
    const loadingIndicator = modal.querySelector('.loader');
    // Создаем объект кеша
    const cache = {};



    let currentVideocardId = null;
    
    if (videocardItemsContainer && modal) {
        videocardItemsContainer.addEventListener('click', (event) => {
            const videocardItem = event.target.closest('.videocard_item');
            if (videocardItem) {
                openModal(event, videocardItem);
            }
        });

        function openModal(event, item) {
            

            loadingIndicator.style.visibility = 'visible';
            infoCard.style.visibility = 'hidden'; 
            modal.style.visibility = 'visible';

            const id = item.getAttribute('data-modal-id');
            const type = item.getAttribute('data-type');

            currentVideocardId = id;
            const cacheKey = `${type}-${id}`;  // Ключ для кеша

            // Проверяем кеш
            if (cache[cacheKey]) {
                updateModalContent(cache[cacheKey]);
            } else {
                // Подгрузка данных из БД с использованием AJAX
                $.ajax({
                    type: 'GET',
                    url: `/api/item/`,  // URL вашего API эндпоинта
                    data: {
                        id: id,
                    },
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
            console.log(data);
            document.querySelector('.info-videocard-name').textContent = `${data.name}`;
            document.querySelector('.info-videocard-price').textContent = `${data.price} $`;
            document.querySelector('.info-videocard-performance').textContent = `Доход ${data.attributes.performance}$  / день`;
             
            loadingIndicator.style.visibility = 'hidden';
            infoCard.style.visibility = 'visible';
            modal.style.visibility = 'visible';
        }

        function closeModal() {
            modal.style.visibility = 'hidden';
            infoCard.style.visibility = 'hidden';
            loadingIndicator.style.visibility = 'hidden';
        }

        window.addEventListener('click', (event) => {
            if (!modal.contains(event.target) && !event.target.closest('.videocard_item')) {
                closeModal();
            }
        });

        // Добавляем обработчик для кнопки покупки
        if (acceptBuyVideocardButton) {
            acceptBuyVideocardButton.addEventListener('click', function() {

                loadingIndicator.style.visibility = 'visible'; // Показываем индикатор загрузки

                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                console.log(currentVideocardId)
                $.ajax({
                    url: '/api/buy_item/',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken // Добавляем CSRF-токен
                    },
                    contentType: 'application/json',
                    data: JSON.stringify({ id: currentVideocardId }), // Преобразуем объект в JSON
                    beforeSend: function () {
                        loadingIndicator.style.visibility = 'visible'; // Показываем индикатор загрузки
                    },
                    success: function (data) {
                        loadingIndicator.style.visibility = 'hidden'; // Скрываем индикатор загрузки
                
                        if (data.success) {
                            closeModal(); // Закрываем модальное окно при успехе
                        }
                    },
                    error: function (xhr, status, error) {
                        loadingIndicator.style.visibility = 'hidden'; // Скрываем индикатор загрузки
                        console.error('Ошибка:', error); // Обработка ошибок
                    }
                });
                
            });
        } else {
            console.error('Кнопка покупки не найдена');
        }
    } else {
        console.error('Один из элементов не найден: videocardItemsContainer или modal');
    }
});
