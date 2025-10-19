
const fileSelect = document.getElementById('file-select');
const sheetSelect = document.getElementById('sheet-select');
const generateBtn = document.getElementById('generate-btn');
const reportTable = document.getElementById('report-table');
const reportBody = document.getElementById('report-body');
const placeholder = document.getElementById('placeholder');

// 1. Загрузить список файлов
async function loadFiles() {
    try {
        const res = await fetch('/v1/upload');
        const files = await res.json();
        fileSelect.innerHTML = '<option value="">—</option>';
        files.forEach(f => {
            if (f.extension === '.xlsx' || f.extension === '.xls') {
                const opt = document.createElement('option');
                opt.value = f.id;
                opt.textContent = `${f.name}${f.extension}`;
                opt.dataset.extension = f.extension;
                fileSelect.appendChild(opt);
            }
        });
    } catch (e) {
        console.error("Ошибка загрузки файлов:", e);
    }
}

// 2. При выборе файла — загрузить листы
fileSelect.addEventListener('change', async () => {
    const fileId = fileSelect.value;
    sheetSelect.disabled = !fileId;
    sheetSelect.innerHTML = '<option value="">Загрузка...</option>';
    generateBtn.disabled = true;

    if (!fileId) {
        sheetSelect.innerHTML = '<option value="">Сначала выберите файл</option>';
        return;
    }

    try {
        const res = await fetch(`/v1/upload/${fileId}`);
        const file = await res.json();
        sheetSelect.innerHTML = '';
        if (file.sheet && file.sheet.length > 0) {
            file.sheet.forEach(sheet => {
                const opt = document.createElement('option');
                opt.value = sheet;
                opt.textContent = sheet;
                sheetSelect.appendChild(opt);
            });
        } else {
            sheetSelect.innerHTML = '<option value="">Нет листов</option>';
        }
    } catch (e) {
        sheetSelect.innerHTML = '<option value="">Ошибка</option>';
        console.error("Ошибка загрузки листов:", e);
    }
});

// 3. При выборе листа — разблокировать кнопку
sheetSelect.addEventListener('change', () => {
    generateBtn.disabled = !sheetSelect.value;
});

// 4. Генерация отчёта
generateBtn.addEventListener('click', async () => {
    const fileId = fileSelect.value;
    const sheetName = sheetSelect.value;
    const extension = fileSelect.selectedOptions[0]?.dataset.extension;

    const url = `/v1/report/${fileId}/generate-report?extension=${encodeURIComponent(extension)}&sheet_name=${encodeURIComponent(sheetName)}`;

    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        reportBody.innerHTML = '';
        Object.entries(data)
            .sort((a, b) => b[1] - a[1])
            .forEach(([rso, amount]) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${rso}</td><td style="text-align: right;">${Number(amount).toFixed(2)}</td>`;
                reportBody.appendChild(tr);
            });

        reportTable.style.display = 'table';
        placeholder.style.display = 'none';

    } catch (e) {
        alert("Ошибка генерации отчёта: " + e.message);
    }
});

// Запуск
document.addEventListener('DOMContentLoaded', loadFiles);
