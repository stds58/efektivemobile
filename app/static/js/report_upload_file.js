const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');

uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) {
        alert('Выберите файл для загрузки');
        return;
    }

    // Проверим расширение (опционально)
    const allowed = ['.xlsx', '.xls'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowed.includes(ext)) {
        alert('Разрешены только файлы .xlsx и .xls');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/v1/upload', {
            method: 'POST',
            body: formData
            // Не указываем Content-Type — браузер сам установит с boundary
        });

        if (res.ok) {
            alert('Файл успешно загружен!');
            fileInput.value = ''; // очистить выбор
            loadFiles(); // обновить список файлов
        } else {
            const err = await res.json().catch(() => ({}));
            alert('Ошибка загрузки: ' + (err.detail || 'Неизвестная ошибка'));
        }
    } catch (e) {
        console.error('Ошибка сети:', e);
        alert('Не удалось подключиться к серверу');
    }
});
