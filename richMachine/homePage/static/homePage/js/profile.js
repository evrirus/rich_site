document.addEventListener('DOMContentLoaded', () => {
    const nickname = document.querySelector('.nickname span.edited');
    const modal = document.getElementById('nicknameModal');
    const input_nickname = document.querySelector('input #new_nickname');
    const closeNicknameButton = document.getElementById('close_nickname');

    if (nickname && modal && closeNicknameButton) {
        nickname.addEventListener('click', (event) => {
            openModal(event);
        });

        function openModal(event) {
            modal.style.visibility = 'visible';
            modal.style.left = `${event.offsetX+100}px`;
            modal.style.top = `${event.offsetY+120}px`;
            console.log(event);
        }

        function closeModal() {
            modal.style.visibility = 'hidden';
        }

        closeNicknameButton.addEventListener('click', () => {
            closeModal();
        });

        window.addEventListener('click', (event) => {
            // Закрываем модальное окно только если клик произошел вне его контента
            if (!modal.contains(event.target) && event.target !== nickname) {
                closeModal();
            }
        });

        $(document).ready(function() {
            $('#accept_nickname').on('click', function() {
                // Получаем данные формы
                var formData = $('#nickname-form').serialize(); 
                
                // Отправляем AJAX-запрос
                $.ajax({
                    type: 'POST',
                    url: $('#nickname-form').attr('action'),
                    data: formData,
                    success: function(response) {
                        // Проверяем, есть ли у ответа успех
                        if (response.success) {
                            // Обновляем элемент на странице
                            $('#current-name').text(response.new_nickname); // Предполагается, что сервер отправит новый ник
                            closeModal()
                            input_nickname.value = "";
                        } else {
                            alert(response.error); // Если есть ошибка, выводим ее
                        }
                    },
                    error: function(xhr, status, error) {
                        // Обработка ошибок AJAX
                        alert('Произошла ошибка: ' + error);
                    }
                });
            });
        });

        window.openModal = openModal;
        window.closeModal = closeModal;
    } else {
        console.error('Один из элементов не найден: nickname, modal или closeNicknameButton');
    }

});
