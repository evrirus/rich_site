document.addEventListener('DOMContentLoaded', () => {
    const transportItemsContainer = document.querySelector('.property'); 
    const modal = document.querySelector('#transportModal');
    const acceptBuyTransportButton = document.getElementById('accept_buy_transport');

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
            
            modal.style.visibility = 'visible';
            modal.style.left = `${event.layerX}px`; 
            modal.style.top = `${event.layerY}px`; 
        }

        function updateModalContent(data) {
            document.querySelector('.transport-name').textContent = `${data.name}`;
            document.querySelector('.transport-price').textContent = `${data.price} ₽`;
            document.querySelector('.transport-produced').textContent = `Произведено: ${data.produced}`;
            document.querySelector('.transport-quantity').textContent = `В наличии: ${data.quantity}`;
        }

        function closeModal() {
            modal.style.visibility = 'hidden';
        }

        window.addEventListener('click', (event) => {
            if (!modal.contains(event.target) && !event.target.closest('.transport_item')) {
                closeModal();
            }
        });

        // Добавляем обработчик для кнопки покупки
        if (acceptBuyTransportButton) {
            acceptBuyTransportButton.addEventListener('click', function() {
                const loadingIndicator = modal.querySelector('.loading');
                loadingIndicator.style.display = 'block'; // Показываем индикатор загрузки

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
                      loadingIndicator.style.display = 'none'; // Скрываем индикатор загрузки

                      if (data.success) {
                          alert('Покупка прошла успешно!');
                          closeModal();
                      } else {
                          alert('Произошла ошибка при покупке: ' + data.message);
                      }
                  }).catch(error => {
                      loadingIndicator.style.display = 'none'; // Скрываем индикатор загрузки
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
