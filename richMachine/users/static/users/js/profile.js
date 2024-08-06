document.addEventListener('DOMContentLoaded', () => {
    const nickname = document.querySelector('.nickname span.edited');
    const modalNickname = document.getElementById('nicknameModal');
    const input_nickname = document.querySelector('#new_nickname');
    const closeNicknameButton = document.getElementById('close_nickname');

    const carDivs = document.querySelectorAll('.car.frosted_glass');
    const yachtDivs = document.querySelectorAll('.yacht.frosted_glass');
    const houseDivs = document.querySelectorAll('.house.frosted_glass');

    const modalTransport = document.querySelector('#transportModal');
    const modalHouse = document.querySelector('#houseModal');

    const acceptSellTransportButton = document.getElementById('acceptSellTransport');
    const acceptSellHouseButton = document.getElementById('acceptSellHouse');

    const loadingIndicatorTransport = document.querySelector('.transport-modal-content .loader');
    const loadingIndicatorHouse = document.querySelector('.house-modal-content .loader');
    const infoCar = document.querySelector('.info__car');
    const infoHouse = document.querySelector('.info__house');

    const icon_language = document.querySelector('#nickname .icon-language');

    const cache = {};

    let currentTransportId, currentTransportType, currentTransportNumerical;

    function openModal(modal, event, xOffset = -200, yOffset = 0) {
        // Close all other modals
        closeAllModals();
        modal.style.visibility = 'visible';
        if (modal === modalNickname) {
            modal.style.left = `${event.clientX - 350 + xOffset}px`;
        } else {
            modal.style.left = `${event.clientX + xOffset}px`;
        }
        
        modal.style.top = `${event.layerY + yOffset}px`;
    }

    function closeAllModals() {
        [modalNickname, modalTransport, modalHouse].forEach(modal => {
            if (modal) modal.style.visibility = 'hidden';
        });
        if (infoCar) infoCar.style.visibility = 'hidden';
        if (infoHouse) infoHouse.style.visibility = 'hidden';
    }

    function updateModalContent(data, type) {
        if (type === 'transport') {
            document.querySelector('.transport-name').textContent = `${data.name}`;
            document.querySelector('.transport-price').textContent = `${data.price} ₽`;
            document.querySelector('.transport-produced').textContent = `Произведено: ${data.maxQuantity}`;
            document.querySelector('.transport-quantity').textContent = `В продаже: ${data.quantity}`;
            document.querySelector('.transport-plate').textContent = `Номера: ${data.plate}`;

            loadingIndicatorTransport.style.visibility = 'hidden';
            infoCar.style.visibility = 'visible';
        } else if (type === 'house') {
            document.querySelector('.house-district-name').textContent = data.district_info.name;
            document.querySelector('.house-type').textContent = `${data.type} №`;
            document.querySelector('#house_id_district').textContent = data.id_for_district;
            document.querySelector('#house_id').textContent = data.id;
            document.querySelector('#house_price').textContent = `${data.price} ₽`;
            document.querySelector('#house_basement').innerHTML = data.basement;
            document.querySelector('#house_floors').textContent = data.floors;
            document.querySelector('#house_class').textContent = data.class;
            
            loadingIndicatorHouse.style.visibility = 'hidden';
            infoHouse.style.visibility = 'visible';
        }
    }

    function openTransportModal(event, item) {
        openModal(modalTransport, event);

        currentTransportId = item.getAttribute('data-modal-id');
        currentTransportType = item.getAttribute('data-modal-type');
        currentTransportNumerical = item.getAttribute('numerical-order');

        const cacheKey = `${currentTransportType}-${currentTransportId}`;

        infoCar.style.visibility = 'hidden';
        loadingIndicatorTransport.style.visibility = 'visible';

        if (cache[cacheKey]) {
            updateModalContent(cache[cacheKey], 'transport');
        } else {
            $.ajax({
                type: 'GET',
                url: `/users/get_transport_profile/${currentTransportType}/${currentTransportId}/${currentTransportNumerical}/`,
                success: function(response) {
                    cache[cacheKey] = response;
                    updateModalContent(response, 'transport');
                },
                error: function(xhr, status, error) {
                    console.error('Ошибка при загрузке данных: ', error);
                    loadingIndicatorTransport.style.visibility = 'hidden';
                }
            });
        }
    }

    function openHouseModal(event, item) {
        openModal(modalHouse, event);
        currentHouseId = item.getAttribute('data-modal-id');

        const cacheKey = `house-${currentHouseId}`;

        infoHouse.style.visibility = 'hidden';
        loadingIndicatorHouse.style.visibility = 'visible';

        if (cache[cacheKey]) {
            updateModalContent(cache[cacheKey], 'house');
        } else {
            $.ajax({
                type: 'GET',
                url: `/users/get_house_profile/${currentHouseId}/`,
                success: function(response) {
                    cache[cacheKey] = response;
                    updateModalContent(response, 'house');
                },
                error: function(xhr, status, error) {
                    console.error('Ошибка при загрузке данных: ', error);
                    loadingIndicatorHouse.style.visibility = 'hidden';
                }
            });
        }
    }

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

    if (nickname && modalNickname && closeNicknameButton) {
        nickname.addEventListener('dblclick', (event) => openModal(modalNickname, event, 40, 30));
        closeNicknameButton.addEventListener('click', closeAllModals);
    
        $(document).ready(function() {
            $('#nickname-form').on('submit', function(event) {
                event.preventDefault(); // отменяем стандартное поведение отправки формы
    
                const formData = $(this).serialize();

                $.ajax({
                    type: 'POST',
                    url: "/users/change_nickname/",
                    data: formData,
                    success: function(response) {
                        if (response.success) {
                            $('#current-name').text(response.new_nickname);
                            closeAllModals();
                            $('#new_nickname').val(""); // очищаем input поле
                        } else {
                            console.log(response.success)
                            alert(response.error);
                        }
                        handleMessages(response.messages);
                    },
                    error: function(xhr, status, error) {
                        alert('Произошла ошибка: ' + error);
                    }
                });
            });
    
            $('#accept_nickname').on('click', function() {
                $('#nickname-form').submit(); // триггерим событие отправки формы
            });
        });
    }
    
    

    function handleTransportClick(event) {
        openTransportModal(event, this);
    }

    if (modalTransport && (carDivs.length || yachtDivs.length)) {
        carDivs.forEach(element => element.addEventListener('click', handleTransportClick));
        yachtDivs.forEach(element => element.addEventListener('click', handleTransportClick));

        if (acceptSellTransportButton) {
            acceptSellTransportButton.addEventListener('click', function() {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                fetch(`/users/sell_transport/${currentTransportType}/${currentTransportId}/${currentTransportNumerical}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        id: currentTransportId,
                        type: currentTransportType
                    })
                }).then(response => response.json())
                  .then(data => {
                    loadingIndicatorTransport.style.visibility = 'hidden';
                      if (data.success) {
                          alert('Покупка прошла успешно!');
                          closeAllModals();
                      } else {
                          alert('Произошла ошибка при покупке: ' + data.message);
                      }
                  }).catch(error => {
                    loadingIndicatorTransport.style.visibility = 'hidden';
                      alert('Произошла ошибка: ' + error.message);
                  });
            });
        }
    }

    if (houseDivs && modalHouse) {
        houseDivs.forEach(element => element.addEventListener('click', (event) => openHouseModal(event, element)));

        if (acceptSellHouseButton) {
            acceptSellHouseButton.addEventListener('click', function() {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                fetch(`/users/sell_house/${currentHouseId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        id: currentHouseId,
                    })
                }).then(response => response.json())
                  .then(data => {
                    loadingIndicatorTransport.style.visibility = 'hidden';
                      if (data.success) {
                          alert('Продажа прошла успешно!');
                          closeAllModals();
                      } else {
                          alert('Произошла ошибка при продаже: ' + data.message);
                      }
                  }).catch(error => {
                    loadingIndicatorTransport.style.visibility = 'hidden';
                      alert('Произошла ошибка: ' + error.message);
                  });
            });
        }
    }

    window.addEventListener('click', (event) => {
        if (!modalTransport.contains(event.target) && !modalHouse.contains(event.target) && !modalNickname.contains(event.target) && !event.target.closest('.car.frosted_glass') && !event.target.closest('.yacht.frosted_glass') && !event.target.closest('.house.frosted_glass')) {
            closeAllModals();
        }
    });

    window.openModal = openModal;
    window.closeAllModals = closeAllModals;
    window.openTransportModal = openTransportModal;
    window.openHouseModal = openHouseModal;


    if (icon_language) {
        icon_language.addEventListener('dblclick', (event) => {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(`/users/change_language/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            }).then(response => response.json())
              .then(data => {
                    if (data.success) {
                        if (data.new_language === "ru") {
                            icon_language.src = '/static/users/img/russia.svg';
                        } else {
                            icon_language.src = '/static/users/img/eng.svg';
                        }
                        closeAllModals();
                    }
                    handleMessages(data.messages);
            }).catch(error => {
                alert('Произошла ошибка: ' + error.message);
            });
        });
    }
});
