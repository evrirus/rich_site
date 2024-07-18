document.addEventListener('DOMContentLoaded', () => {
    const transportItemsContainer = document.querySelector('.property'); 
    const modal = document.querySelector('#transportModal');

    // Создаем объект кеша
    const cache = {};

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
            document.querySelector('.transport-name').textContent = data.name;
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
    } else {
        console.error('Один из элементов не найден: transportItemsContainer или modal');
    }
});
