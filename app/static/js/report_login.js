const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const loginForm = document.getElementById('login-form');

// Функция: показать форму входа
function showLogin() {
    loginForm.style.display = 'flex';
    logoutBtn.style.display = 'none';
}

// Функция: показать кнопку выхода
function showLogout() {
    loginForm.style.display = 'none';
    logoutBtn.style.display = 'inline-block';
}

// Вход
loginBtn.addEventListener('click', async () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
        alert('Введите email и пароль');
        return;
    }

    try {
        const res = await fetch('/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (res.ok) {
            //alert('Успешный вход!');
            showLogout(); // ← скрываем форму, показываем "Выйти"
            loadFiles();  // обновляем список файлов
        } else {
            const err = await res.json().catch(() => ({}));
            alert('Ошибка входа: ' + (err.detail || 'Неверные данные'));
        }
    } catch (e) {
        alert('Не удалось подключиться к серверу');
    }
});

// Выход
logoutBtn.addEventListener('click', async () => {
    try {
        const res = await fetch('/v1/auth/logout', {
            method: 'POST'
        });

        if (res.ok) {
            //alert('Вы вышли из системы');
            showLogin(); // ← возвращаем форму входа

            // Очистка отчёта
            document.getElementById('report-body').innerHTML = '';
            document.getElementById('report-table').style.display = 'none';
            document.getElementById('placeholder').style.display = 'block';
            document.getElementById('file-select').innerHTML = '<option value="">—</option>';
            document.getElementById('sheet-select').innerHTML = '<option value="">Сначала выберите файл</option>';
            document.getElementById('sheet-select').disabled = true;
            document.getElementById('generate-btn').disabled = true;
        } else {
            alert('Не удалось выйти');
        }
    } catch (e) {
        alert('Ошибка при выходе');
    }
});