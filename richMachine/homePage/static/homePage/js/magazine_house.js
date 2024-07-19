document.addEventListener('DOMContentLoaded', () => {
    const houseItemsContainer = document.querySelector('.property'); 
    const modal = document.querySelector('#houseModal');
    const acceptBuyHouseButton = document.getElementById('accept_buy_house');

    // Создаем объект кеша
    const cache = {};

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
            modal.style.visibility = 'visible';
            modal.style.left = `${event.layerX}px`; 
            modal.style.top = `${event.layerY}px`; 
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
            
            
        }

        function updateModalContent(data) {
            console.log(data)
            document.querySelector('.house-district-name').textContent = `${data.district_name}`;
            document.querySelector('.house-type').textContent = `${data.house_type} №`;
            document.querySelector('#house_id_district').textContent = `${data.house_id_for_district}`;


            // document.querySelector('#house_id_header').textContent = `${data.quantity}`;
            document.querySelector('#house_id').textContent = `${data.house_id}`;

            // document.querySelector('#house_price_header').textContent = `${data.name}`;
            document.querySelector('#house_price').textContent = `${data.house_price} ₽`;

            // document.querySelector('#house_basement_header').textContent = `${data.produced}`;
            document.querySelector('#house_basement').innerHTML = `${data.house_basement}`;
            // document.querySelector('#level_basement').textContent = `${data.house_basement_level}`;
            
            // document.querySelector('#house_floors_header').textContent = `${data.quantity}`;
            document.querySelector('#house_floors').textContent = `${data.house_floor}`;
            
            // document.querySelector('#house_class_header').textContent = `${data.quantity}`;
            document.querySelector('#house_class').textContent = `${data.house_class}`;
        }

        function closeModal() {
            modal.style.visibility = 'hidden';
        }

        window.addEventListener('click', (event) => {
            if (!modal.contains(event.target) && !event.target.closest('.house_item')) {
                closeModal();
            }
        });

        // Добавляем обработчик для кнопки покупки
        if (acceptBuyHouseButton) {
            acceptBuyHouseButton.addEventListener('click', function() {
                // const loadingIndicator = modal.querySelector('.loading');
                // loadingIndicator.style.display = 'block'; // Показываем индикатор загрузки

                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch(`../buy_house/${currentHouseId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        id: currentHouseId
                    })
                }).then(response => response.json())
                  .then(data => {
                    //   loadingIndicator.style.display = 'none'; // Скрываем индикатор загрузки

                      if (data.success) {
                          alert('Покупка прошла успешно!');
                          closeModal();
                      } else {
                          alert('Произошла ошибка при покупке: ' + data.message);
                      }
                  }).catch(error => {
                    //   loadingIndicator.style.display = 'none'; // Скрываем индикатор загрузки
                      alert('Произошла ошибка: ' + error.message);
                  });
            });
        } else {
            console.error('Кнопка покупки не найдена');
        }
    } else {
        console.error('Один из элементов не найден: houseItemsContainer или modal');
    }
});
