document.addEventListener('DOMContentLoaded', () => {
    const nickname = document.querySelector('.nickname span.edited');
    const modalNickname = document.getElementById('nicknameModal');
    const input_nickname = document.querySelector('#new_nickname');
    const closeNicknameButton = document.getElementById('close_nickname');

    const carDivs = document.querySelectorAll('.car.frosted_glass');
    const modalTransport = document.querySelector('#transportModal');

    const acceptSellTransportButton = document.getElementById('acceptSellTransport');
    const acceptSellTransportToPlayerButton = document.getElementById('acceptSellTransportToPlayer');

    const acceptSellHouseButton = document.getElementById('acceptSellHouse');
    const acceptSellHouseToPlayerButton = document.getElementById('acceptSellHouseToPlayer');

    const yachtDivs = document.querySelectorAll('.yacht.frosted_glass');
    const modalHouse = document.querySelector('#houseModal');

    const loadingIndicator = document.querySelector('.loader');

    if (nickname && modalNickname && closeNicknameButton) {
        nickname.addEventListener('click', (event) => {
            openNicknameModal(event);
        });

        function openNicknameModal(event) {
            modalNickname.style.visibility = 'visible';
            modalNickname.style.left = `${event.offsetX + 40}px`;
            modalNickname.style.top = `${event.offsetY + 30}px`;
            console.log(event);
        }

        function closeNicknameModal() {
            modalNickname.style.visibility = 'hidden';
        }

        closeNicknameButton.addEventListener('click', () => {
            closeNicknameModal();
        });

        window.addEventListener('click', (event) => {
            if (!modalNickname.contains(event.target) && event.target !== nickname) {
                closeNicknameModal();
            }
        });

        $(document).ready(function() {
            $('#accept_nickname').on('click', function() {
                var formData = $('#nickname-form').serialize();
                $.ajax({
                    type: 'POST',
                    url: $('#nickname-form').attr('action'),
                    data: formData,
                    success: function(response) {
                        if (response.success) {
                            $('#current-name').text(response.new_nickname);
                            closeNicknameModal();
                            input_nickname.value = "";
                        } else {
                            alert(response.error);
                        }
                    },
                    error: function(xhr, status, error) {
                        alert('Произошла ошибка: ' + error);
                    }
                });
            });
        });

        window.openNicknameModal = openNicknameModal;
        window.closeNicknameModal = closeNicknameModal;
    }






    if (modalTransport && carDivs) {
        carDivs.forEach(element => {
            element.addEventListener('click', event => {
                openTransportModal(event, element);
            });
        });

        function openTransportModal(event, item) {
            modalTransport.style.visibility = 'visible';
            modalTransport.style.left = `${event.layerX + 90}px`;
            modalTransport.style.top = `${event.layerY + 60}px`;
            const id = item.getAttribute('data-modal-id');
            const type = item.getAttribute('data-modal-type');
            const numerical_order = item.getAttribute('numerical-order');

            currentTransportId = id;
            currentTransportType = type;
            currentTransportNumerical = numerical_order;
            console.log(event);
        }

        function closeTransportModal() {
            modalTransport.style.visibility = 'hidden';
        }

        window.addEventListener('click', (event) => {
            if (!modalTransport.contains(event.target) && !event.target.closest('.car.frosted_glass')) {
                closeTransportModal();
            }
        });

        // Добавляем обработчик для кнопки покупки
        if (acceptSellTransportButton) {
            console.log(acceptSellTransportButton);
            acceptSellTransportButton.addEventListener('click', function() {
                // loadingIndicator.style.visibility = 'visible'; // Показываем индикатор загрузки

                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                console.log(currentTransportType, currentTransportId)
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
                      loadingIndicator.style.visibility = 'hidden'; // Скрываем индикатор загрузки

                      if (data.success) {
                          alert('Покупка прошла успешно!');
                          closeTransportModal();
                      } else {
                          alert('Произошла ошибка при покупке: ' + data.message);
                      }
                  }).catch(error => {
                      loadingIndicator.style.visiblity = 'hidden';
                      alert('Произошла ошибка: ' + error.message);
                  });
            });

        window.openTransportModal = openTransportModal;
        window.closeTransportModal = closeTransportModal;
    }

}});
