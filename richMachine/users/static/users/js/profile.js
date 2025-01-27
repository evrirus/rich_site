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

    const btnSellTransportToPlayer = $('#acceptSellTransportToPlayer')
    const sellToPlayerTransportModal = $('#sellToPlayerTransportModal')
    const acceptSellToPlayerButton = $('#accept_sellToPlayer')
    const inputSellToPlayer = $('#price')

    const acceptSellTransportButton = $('#acceptSellTransport');
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
        if (loadingIndicatorHouse.style.visibility === 'visible') loadingIndicatorHouse.style.visibility = 'hidden';
        if (sellToPlayerTransportModal) sellToPlayerTransportModal.css('visibility', 'hidden')
    }

    function updateModalContent(data, type) {

        if (type === 'transport') {

            document.querySelector('.transport-name').textContent = `${data.info.name}`;
            document.querySelector('.transport-price').textContent = `${formatNumberWithSpaces(data.info.price)} ₽`;
            document.querySelector('.transport-produced').textContent = `Произведено: ${data.info.maxQuantity}`;
            document.querySelector('.transport-quantity').textContent = `В продаже: ${data.info.quantity}`;
            document.querySelector('.transport-plate').textContent = `Номера: ${data.info.plate}`;

            loadingIndicatorTransport.style.visibility = 'hidden';
            infoCar.style.visibility = 'visible';

        } else if (type === 'house') {
            let basement = "Отсутствует";
            if (data.basement > 0) {
                basement = `Имеется[<span style='color: rgb(255, 28, 28);'>lvl</span>=${data.basement}]`;
            }

            document.querySelector('.house-district-name').textContent = data.district_info.name;
            document.querySelector('.house-type').textContent = `${data.type} №`;
            document.querySelector('#house_id_district').textContent = data.id_for_district;
            document.querySelector('#house_id').textContent = data.id;
            document.querySelector('#house_price').textContent = `${formatNumberWithSpaces(data.price)} ₽`;
            document.querySelector('#house_basement').innerHTML = basement;
            document.querySelector('#house_floors').textContent = data.floors;
            document.querySelector('#house_class').textContent = data.class;
            document.querySelector('#basement').setAttribute('house_id', data.id);
            
            loadingIndicatorHouse.style.visibility = 'hidden';
            infoHouse.style.visibility = 'visible';
        }
    }

    function openTransportModal(event, item) {
        openModal(modalTransport, event);

        currentTransportId = item.getAttribute('data-modal-id');
        currentTransportType = item.getAttribute('data-modal-type');
        currentTransportNumerical = item.getAttribute('numerical-order');
        currentTransportUcode = item.getAttribute('ucode');

        const cacheKey = `${currentTransportType}-${currentTransportId}-${currentTransportUcode}`;

        infoCar.style.visibility = 'hidden';
        $('#loadingIndicatorTransport').css('visibility', 'visible');

        if (cache[cacheKey]) {
            updateModalContent(cache[cacheKey], 'transport');
        } else {
            $.ajax({
                type: 'GET',
                url: `/api/transport_info?type=${currentTransportType}&ucode=${currentTransportUcode}&id=${currentTransportId}`,
                success: function(response) {
                    cache[cacheKey] = response;
                    updateModalContent(response, 'transport');
                },
                error: function(xhr, status, error) {
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
                url: `/api/get_house/${currentHouseId}/`,
                success: function(response) {
                    if (!response.success) {
                        loadingIndicatorHouse.style.visibility = 'visible';
                        closeAllModals()

                    }
                    else {

                        cache[cacheKey] = response;
                        updateModalContent(response, 'house');
                    }
                },
                error: function(xhr, status, error) {
                    loadingIndicatorHouse.style.visibility = 'hidden';
                }
            });
        }
    }


    if (nickname && modalNickname && closeNicknameButton) {
        nickname.addEventListener('dblclick', (event) => openModal(modalNickname, event, 40, 30));
        closeNicknameButton.addEventListener('dblclick', closeAllModals);
    
        $(document).ready(function() {
            $('#nickname-form').on('submit', function(event) {
                event.preventDefault(); // отменяем стандартное поведение отправки формы
    
                const formData = $(this).serialize();

                $.ajax({
                    type: 'POST',
                    url: "/api/change_nickname/",
                    data: formData,
                    success: function(response) {

                        if (response.success) {
                            $('#current-name').text(response.new_nickname);
                            $('#new_nickname').val(""); // очищаем input поле
                        }

                        closeAllModals();
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

        if (btnSellTransportToPlayer) {
            btnSellTransportToPlayer.on('click', function() {
                sellToPlayerTransportModal.css('visibility', 'visible');
            })
        }
        if (acceptSellToPlayerButton) {
            acceptSellToPlayerButton.on('click', function() {

                let priceValue = inputSellToPlayer.val().replaceAll(/s/g, '');
                inputSellToPlayer.val(priceValue);
                console.log(currentTransportType, currentTransportId, currentTransportUcode);

                let dataForm = $(this.form).serializeArray();
                let jsonData = {};
                dataForm.forEach(item => {
                    jsonData[item.name] = item.value;
                });

                jsonData['type'] = currentTransportType;
                jsonData['id'] = currentTransportId;
                jsonData['ucode'] = currentTransportUcode;

                jsonData['price'] = jsonData['price'].replaceAll(/\s/g,'')


                if (!jsonData['price'] || jsonData['price'].trim() === '') {
                    return handleMessages('Цена не может быть пустой.');
                } else if (isNaN(jsonData['price'])) {
                    return handleMessages('Цена должна быть числом.');
                } else if (parseInt(jsonData['price'], 10) === 0) {
                    return handleMessages('Цена не может быть равна нулю.');
                } else if (parseInt(jsonData['price'], 10) < 1000) {
                    return handleMessages('Цена не может быть меньше тысячи.');
                }


                const csrfToken = $('[name=csrfmiddlewaretoken]').val();

                $.ajax({
                    url: '/api/sell_transport_to_player/',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify(jsonData),
                    success: function(response) {

                        if (response.success) {
                            const transportDiv = $(`.${currentTransportType}.frosted_glass[ucode="${currentTransportUcode}"][data-modal-type="${currentTransportType}"][numerical-order="${currentTransportNumerical}"]`);
                            transportDiv.remove();
                        }
                        else {
                            handleMessages('Произошла ошибка|' + response.error);
                        }

                        closeAllModals();
                    },
                    error: function(error) {

                        handleMessages('Произошла ошибка|' + (error.responseJSON.error || error.error));
                    }
                });
            });
        }



        if (acceptSellTransportButton) {
            acceptSellTransportButton.on('click', function() {

                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const url = `/api/sell_transport_to_state/${currentTransportType}/${currentTransportUcode}/`;

                const data = {
                    id: currentTransportId,
                    type: currentTransportType
                };
        
                // Using jQuery AJAX
                $.ajax({
                    url: url,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify(data),
                    success: function(response) {
                        loadingIndicatorTransport.style.visibility = 'hidden';
                        if (response.success) {
                            const transportDiv = $(`.${currentTransportType}.frosted_glass[ucode="${currentTransportUcode}"][data-modal-type="${currentTransportType}"][numerical-order="${currentTransportNumerical}"]`);
                            transportDiv.remove();
                        }

                        closeAllModals();

                    },
                    error: function(error) {
                        loadingIndicatorTransport.style.visibility = 'hidden';
                        alert('Произошла ошибка: ' + error.responseJSON.message || error.message); 
                    }
                });
            });
        }
    }

    if (houseDivs && modalHouse) {
        houseDivs.forEach(element => element.addEventListener('click', (event) => openHouseModal(event, element)));

        // Перенаправляет на страницу подвала по ID дома
        document.getElementById('basement').addEventListener('click', function(event) {
            let houseId = event.explicitOriginalTarget.attributes.house_id.textContent;
            window.location.assign(`/basement/${houseId}`);
        });

        if (acceptSellHouseButton) {
            acceptSellHouseButton.addEventListener('click', function() {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                fetch(`/api/sell_house/${currentHouseId}/`, {
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
                              const houseDiv = document.querySelector(`.house.frosted_glass[id="${currentHouseId}"][data-modal-type="house"]`);
                              houseDiv.remove();
                          }


                      closeAllModals();
                    }).catch(error => {
                      loadingIndicatorTransport.style.visibility = 'hidden';
                        alert('Произошла ошибка: ' + error.message);
                    });
            });
        }
    }

    if (acceptSellTransportToPlayer)

    window.addEventListener('click', (event) => {

        let sTPTM = document.getElementById('sellToPlayerTransportModal');

        if (
            !modalTransport.contains(event.target) &&
            !modalHouse.contains(event.target) &&
            !modalNickname.contains(event.target) &&
            !event.target.closest('.car.frosted_glass') &&
            !event.target.closest('.yacht.frosted_glass') &&
            !event.target.closest('.house.frosted_glass') &&
            !sTPTM.contains(event.target)
        ) {
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
            
            fetch(`/api/change_language/`, {
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

            }).catch(error => {
                alert('Произошла ошибка: ' + error.message);
            });
        });
    }
});
