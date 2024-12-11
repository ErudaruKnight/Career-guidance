const questions = [
    { id: 1, text: "Мне нравится работать с инструментами или техникой.", category: "Realistic" },
    { id: 2, text: "Мне интересно изучать научные теории или решать сложные задачи.", category: "Investigative" },
    { id: 3, text: "Я люблю творить: писать, рисовать или заниматься музыкой.", category: "Artistic" },
    { id: 4, text: "Мне нравится помогать другим людям и решать их проблемы.", category: "Social" },
    { id: 5, text: "Я люблю управлять, планировать и добиваться целей.", category: "Enterprising" },
    { id: 6, text: "Мне нравится работать с цифрами или данными.", category: "Conventional" },
    { id: 7, text: "Я предпочитаю проводить время в больших компаниях.", category: "Extroversion" },
    { id: 8, text: "Мне нравится размышлять в одиночестве.", category: "Introversion" },
    { id: 9, text: "Я ориентируюсь на факты и детали.", category: "Sensing" },
    { id: 10, text: "Я доверяю своей интуиции.", category: "Intuition" },
    { id: 11, text: "Я принимаю решения на основе логики.", category: "Thinking" },
    { id: 12, text: "Я принимаю решения на основе чувств.", category: "Feeling" },
    { id: 13, text: "Мне нравится организованный подход.", category: "Judging" },
    { id: 14, text: "Я предпочитаю гибкость и импровизацию.", category: "Perceiving" }
];

let currentIndex = 0; // Индекс текущего вопроса
let answers = []; // Хранилище ответов
let userData = {}; // Данные пользователя

document.addEventListener('DOMContentLoaded', () => {
    const userInfoSection = document.getElementById('user-info-section');
    const startSection = document.getElementById('start-section');
    const descriptionSection = document.getElementById('description-section');
    const testSection = document.getElementById('test-section');
    const questionText = document.getElementById('question-text');
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    const graphSection = document.getElementById('graph-section');
    const userForm = document.getElementById('userForm');

    // Обработка формы пользователя
    userForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const userName = document.getElementById('userName').value.trim();
        const userEmail = document.getElementById('userEmail').value.trim();

        if (validateEmail(userEmail)) {
            userData = { name: userName, email: userEmail };
            userInfoSection.style.display = 'none';
            startSection.style.display = 'block';
        } else {
            alert('Введите корректный email!');
        }
    });

    // Запуск теста
    document.getElementById('startTestButton').addEventListener('click', () => {
        startSection.style.display = 'none';
        descriptionSection.style.display = 'none'; // Скрыть описание
        testSection.style.display = 'block';
        showQuestion();
    });

    // Показать текущий вопрос
    function showQuestion() {
        if (currentIndex < questions.length) {
            questionText.textContent = questions[currentIndex].text;
        } else {
            finishTest();
        }
    }

    // Сохранить ответ и перейти к следующему вопросу
    window.answerQuestion = (score) => {
        answers.push({ category: questions[currentIndex].category, score });
        currentIndex++;
        showQuestion();
    };

    // Завершение теста
    function finishTest() {
        testSection.style.display = 'none';
        resultsSection.style.display = 'block';

        console.log('Отправляемые данные:', { user: userData, answers });

        fetch('/api/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user: userData, answers })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ошибка! Статус: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Полученные данные от сервера:', data);

                if (!data || (!data.RIASEC && !data.MBTI)) {
                    resultsContainer.innerHTML = '<p>Не удалось получить результаты. Пожалуйста, попробуйте снова.</p>';
                    return;
                }

                displayResults(data);
                graphSection.style.display = 'block';
                displayGraph(data);
            })
            .catch(error => {
                console.error('Ошибка при получении данных:', error);
                resultsContainer.innerHTML = '<p>Произошла ошибка при обработке данных. Пожалуйста, попробуйте позже.</p>';
            });
    }

    // Отображение результатов
    function displayResults(data) {
        resultsContainer.innerHTML = '<h3>RIASEC</h3>';

        if (data.RIASEC && data.RIASEC.length > 0) {
            const translations = {
                "Realistic": "Реалистичный",
                "Investigative": "Исследовательский",
                "Artistic": "Артистический",
                "Social": "Социальный",
                "Enterprising": "Предприимчивый",
                "Conventional": "Конвенциональный"
            };

            data.RIASEC.forEach(r => {
                const translatedCategory = translations[r.category] || r.category;
                const p = document.createElement('p');
                p.textContent = `${translatedCategory}: ${r.score}`;
                resultsContainer.appendChild(p);
            });
        } else {
            resultsContainer.innerHTML += '<p>Результаты RIASEC не найдены.</p>';
        }

        // Отображение MBTI
        resultsContainer.innerHTML += '<h3>MBTI</h3>';
        if (data.MBTI) {
            const mbtiType = data.MBTI?.type || 'Unknown';
            const mbtiDescription = data.MBTI?.description || 'Нет описания.';
            resultsContainer.innerHTML += `<p>Тип личности MBTI: <b>${mbtiType}</b></p>`;
            resultsContainer.innerHTML += `<p>${mbtiDescription}</p>`;
        } else {
            resultsContainer.innerHTML += '<p>Результаты MBTI не найдены.</p>';
        }

        resultsContainer.innerHTML += `
            <h3>Анализ и рекомендации</h3>
            <p>${data.Recommendations?.Combined || 'Нет рекомендаций.'}</p>
        `;
    }

    // Построение графика
    function displayGraph(data) {
        const ctx = document.getElementById('mbtiChart').getContext('2d');

        const x = data.MBTI?.axes?.x || 0; // Сенсорика: -1, Интуиция: 1
        const y = data.MBTI?.axes?.y || 0; // Экстраверсия: 1, Интроверсия: -1

        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Тип личности MBTI',
                    data: [{ x: x, y: y }],
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    pointRadius: 20
                }]
            },
            options: {
                plugins: {
                    legend: { display: false },
                    annotation: {
                        annotations: {
                            midlineX: {
                                type: 'line',
                                xMin: 0,
                                xMax: 0,
                                yMin: -2,
                                yMax: 2,
                                borderColor: 'rgba(0, 0, 0, 0.8)',
                                borderWidth: 2
                            },
                            midlineY: {
                                type: 'line',
                                yMin: 0,
                                yMax: 0,
                                xMin: -2,
                                xMax: 2,
                                borderColor: 'rgba(0, 0, 0, 0.8)',
                                borderWidth: 2
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: { display: true, text: 'Сенсорика (влево) — Интуиция (вправо)' },
                        min: -2,
                        max: 2
                    },
                    y: {
                        type: 'linear',
                        position: 'left',
                        title: { display: true, text: 'Интроверсия (вниз) — Экстраверсия (вверх)' },
                        min: -2,
                        max: 2
                    }
                }
            }
        });
    }

    // Проверка email
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});
