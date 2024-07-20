document.addEventListener('DOMContentLoaded', () => {
    const transportItemsContainer = document.querySelector('.property'); 
    const modal = document.querySelector('#transportModal');
    const acceptBuyTransportButton = document.getElementById('accept_buy_transport');
    const infoCar = modal.querySelector('.info__car');

    const loadingIndicator = modal.querySelector('.loader');

    // Создаем объект кеша
    const cache = {};

    let currentTransportType = null;
    let currentTransportId = null;

    if (transportItemsContainer && modal) {
        transportItemsContainer.addEventListener('click', (event) => {
            const transportItem = event.target.closest('.transport_item');
            if (transportItem) {
                openModal(event, transportItem);
            }
        });

        function openModal(event, item) {
            const infoCar = modal.querySelector('.info__car'); // New container for the actual content
            
            loadingIndicator.style.visibility = 'visible';
            infoCar.style.visibility = 'hidden'; // Hide the content initially
            modal.style.visibility = 'visible';

            const id = item.getAttribute('data-modal-id');
            const type = item.getAttribute('data-type');
            currentTransportType = type;
            currentTransportId = id;
            const cacheKey = `${type}-${id}`;  // Ключ для кеша

            // Проверяем кеш
            if (cache[cacheKey]) {
                updateModalContent(cache[cacheKey]);
            } else {
                // Подгрузка данных из БД с использованием AJAX
                $.ajax({
                    type: 'GET',
                    url: `get_transport_info/${type}/${id}/`,  // URL вашего API эндпоинта
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

            document.querySelector('.transport-name').textContent = `${data.name}`;
            document.querySelector('.transport-price').textContent = `${data.price} ₽`;
            document.querySelector('.transport-produced').textContent = `Произведено: ${data.produced}`;
            document.querySelector('.transport-quantity').textContent = `В наличии: ${data.quantity}`;
            
            loadingIndicator.style.visibility = 'hidden';
            infoCar.style.visibility = 'visible'; // Show the content once loaded
            modal.style.visibility = 'visible';
        }

        function closeModal() {
            modal.style.visibility = 'hidden';
            infoCar.style.visibility = 'hidden';
            loadingIndicator.style.visibility = 'hidden';
        }

        window.addEventListener('click', (event) => {
            if (!modal.contains(event.target) && !event.target.closest('.transport_item')) {
                closeModal();
            }
        });

        // Добавляем обработчик для кнопки покупки
        if (acceptBuyTransportButton) {
            acceptBuyTransportButton.addEventListener('click', function() {

                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch(`/magazine/buy_transport/${currentTransportType}/${currentTransportId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        type: currentTransportType,
                        id: currentTransportId
                    })
                }).then(response => response.json())
                  .then(data => {
                        if (data.success) {
                            alert('Покупка прошла успешно!');
                            closeModal();
                        } else {
                            alert('Произошла ошибка при покупке: ' + data.message);
                            // Запрашиваем разрешение на уведомления
                            Notification.requestPermission().then(permission => {
                                if (permission === "granted") {
                                    console.log('Пытаюсь создать уведомление');
                                    const notification = new Notification('Rich Site', {
                                        body: data.message,
                                        // icon: '/static/homePage/img/logo.png'
                                    });
                                } else {
                                    console.log('Разрешение на уведомления не получено');
                                }
                            }).catch(err => {
                                console.error("Ошибка при получении разрешения на уведомления:", err);
                            });
                        }
                }).catch(error => {
                    alert('Произошла ошибка: ' + error.message);
                });
            });
        } else {
            console.error('Кнопка покупки не найдена');
        }
    } else {
        console.error('Один из элементов не найден: transportItemsContainer или modal');
    }
});
