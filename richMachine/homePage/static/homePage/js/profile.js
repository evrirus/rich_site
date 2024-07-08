document.addEventListener('DOMContentLoaded', () => {
    const nickname = document.querySelector('.nickname span.edited');
    const modal = document.getElementById('nicknameModal');
    const closeNicknameButton = document.getElementById('close_nickname');

    if (nickname && modal && closeNicknameButton) {
        nickname.addEventListener('dblclick', (event) => {
            openModal(event.clientX, event.clientY);
        });

        function openModal(x, y) {
            modal.style.display = 'block';
            modal.style.left = `${x-1125}px`;
            modal.style.top = `${y+130}px`;
        }

        function closeModal() {
            modal.style.display = 'none';
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

        window.openModal = openModal;
        window.closeModal = closeModal;
    } else {
        console.error('Один из элементов не найден: nickname, modal или closeNicknameButton');
    }
});
