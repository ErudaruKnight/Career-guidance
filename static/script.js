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

    let currentIndex = 0;
    let answers = [];
    let userData = {};

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

    const answerDescriptions = {
        1: "1 - Совсем не согласен",
        2: "2 - Почти не согласен",
        3: "3 - Не уверен",
        4: "4 - Почти согласен",
        5: "5 - Полностью согласен"
    };

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
        descriptionSection.style.display = 'none';
        testSection.style.display = 'block';
        showQuestion();
    });

    // Показ текущего вопроса
    function showQuestion() {
        if (currentIndex < questions.length) {
            questionText.textContent = questions[currentIndex].text;
            const answerDescription = document.getElementById('answer-description');
            answerDescription.textContent = "Выберите ответ: " + Object.values(answerDescriptions).join(", ");
        } else {
            finishTest();
        }
    }

    // Сохранение ответа
    window.answerQuestion = (score) => {
        answers.push({ category: questions[currentIndex].category, score });
        currentIndex++;
        showQuestion();
    };

    // Завершение теста
    function finishTest() {
        testSection.style.display = 'none';
        resultsSection.style.display = 'block';

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
        resultsContainer.innerHTML = `
            <h3>RIASEC Результаты</h3>
            ${data.RIASEC.map(r => `
                <p><b>${translateCategory(r.category)}:</b> ${r.score} — ${r.description}</p>
            `).join('')}
            
            <h3>MBTI Результаты</h3>
            <p><b>Тип личности MBTI:</b> ${data.MBTI.type || 'Не определён'}</p>
            <p>${data.MBTI.description || 'Описание отсутствует.'}</p>
            
            <h3>Рекомендации</h3>
            <p>${data.Recommendations.MBTI_Analysis}</p>
            <p><b>Рекомендуемые профессии:</b> ${data.Recommendations.MBTI_Professions.join(', ') || 'Нет рекомендаций.'}</p>
        `;
    }
    
    // Функция для перевода категорий
    function translateCategory(category) {
        const translations = {
            "Realistic": "Реалистичный",
            "Investigative": "Исследовательский",
            "Artistic": "Артистический",
            "Social": "Социальный",
            "Enterprising": "Предприимчивый",
            "Conventional": "Конвенциональный"
        };
        return translations[category] || category;
    }
    

    // Построение графика
    function displayGraph(data) {
        const ctx = document.getElementById('mbtiChart').getContext('2d');
    
        // Получение координат x и y из данных
        const x = data.MBTI?.axes?.x || 0; // Сенсорика (-1) / Интуиция (1)
        const y = data.MBTI?.axes?.y || 0; // Экстраверсия (1) / Интроверсия (-1)
    
        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Ваш MBTI профиль',
                    data: [{ x: x, y: y }],
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    pointRadius: 8
                }]
            },
            options: {
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `MBTI (${x.toFixed(2)}, ${y.toFixed(2)})`;
                            }
                        }
                    },
                    annotation: {
                        annotations: {
                            lineX: {
                                type: 'line',
                                xMin: 0,
                                xMax: 0,
                                yMin: -2,
                                yMax: 2,
                                borderColor: 'rgba(0, 0, 0, 0.6)',
                                borderWidth: 1,
                                label: {
                                    display: true,
                                    position: 'end'
                                }
                            },
                            lineY: {
                                type: 'line',
                                yMin: 0,
                                yMax: 0,
                                xMin: -2,
                                xMax: 2,
                                borderColor: 'rgba(0, 0, 0, 0.6)',
                                borderWidth: 1,
                                label: {
                                    display: true,
                                    position: 'end'
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: { display: true, text: 'Сенсорика (-) / Интуиция (+)' },
                        min: -2,
                        max: 2
                    },
                    y: {
                        type: 'linear',
                        position: 'left',
                        title: { display: true, text: 'Интроверсия (-) / Экстраверсия (+)' },
                        min: -2,
                        max: 2
                    }
                }
            }
        });
    }
    

    // Валидация email
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});
