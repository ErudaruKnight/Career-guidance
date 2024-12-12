from flask import Flask, render_template, request, jsonify
import openpyxl
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# Настройки Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'krosspsih@gmail.com'  # Ваш email
app.config['MAIL_PASSWORD'] = 'lizl kdgk ixed vxgd'  # Ваш ключ приложения

mail = Mail(app)

mbti_analysis = {
    "INTJ": {
        "description": "Стратег: Стратегические мыслители с воображением и планом на всё.",
        "professions": ["Стратегический аналитик", "Научный сотрудник", "Проектный менеджер"]
    },
    "INFP": {
        "description": "Посредник: Поэтичные, добрые и альтруистичные личности, готовые помочь.",
        "professions": ["Писатель", "Психолог", "Социальный работник"]
    },
    "ISTP": {
        "description": "Виртуоз: Экспериментаторы, мастера в работе с инструментами.",
        "professions": ["Инженер", "Механик", "Специалист по ремонту"]
    },
    "ENTP": {
        "description": "Полемист: Умные и любопытные мыслители, которые любят интеллектуальные вызовы.",
        "professions": ["Маркетолог", "Консультант по дизайну", "Инновационный менеджер"]
    },
    "INFJ": {
        "description": "Советник: Вдохновляющие идеалисты, которые стремятся к лучшему миру.",
        "professions": ["Психотерапевт", "Учитель", "Социальный активист"]
    },
    "ENFJ": {
        "description": "Наставник: Харизматичные лидеры, мотивирующие и вдохновляющие других.",
        "professions": ["HR-менеджер", "Тренер по развитию", "Руководитель команды"]
    },
    "INTP": {
        "description": "Учёный: Логичные и изобретательные мыслители, ориентированные на знания.",
        "professions": ["Программист", "Исследователь", "Физик"]
    },
    "ENTJ": {
        "description": "Командир: Лидеры с сильным характером, которые создают путь к успеху.",
        "professions": ["Руководитель проекта", "Бизнес-консультант", "Директор компании"]
    },
    "ISFJ": {
        "description": "Защитник: Ответственные и заботливые личности, которые ценят стабильность.",
        "professions": ["Медсестра", "Учитель начальных классов", "Администратор"]
    },
    "ESFJ": {
        "description": "Консул: Заботливые и популярные, всегда готовые помочь другим.",
        "professions": ["Врач", "Социальный работник", "Консультант по работе с клиентами"]
    },
    "ISTJ": {
        "description": "Администратор: Надёжные и организованные, которые любят порядок.",
        "professions": ["Бухгалтер", "Системный администратор", "Юрист"]
    },
    "ESTJ": {
        "description": "Менеджер: Уверенные в себе и преданные своим задачам организаторы.",
        "professions": ["Руководитель отдела", "Финансовый аналитик", "Менеджер проекта"]
    },
    "ISFP": {
        "description": "Артист: Тихие и добрые экспериментаторы, ищущие вдохновение в жизни.",
        "professions": ["Фотограф", "Дизайнер", "Художник"]
    },
    "ESFP": {
        "description": "Развлекатель: Живые и энергичные, создающие радость вокруг себя.",
        "professions": ["Актёр", "Музыкант", "Организатор мероприятий"]
    },
    "ESTP": {
        "description": "Делец: Смелые и энергичные, которые ориентированы на действие.",
        "professions": ["Предприниматель", "Торговый представитель", "Пилот"]
    },
    "ENFP": {
        "description": "Борец: Творческие и энтузиастичные личности с оптимистичным взглядом на жизнь.",
        "professions": ["Журналист", "Коуч", "Организатор мероприятий"]
    }
}


# Путь к Excel-файлу
EXCEL_FILE = os.path.join(os.getcwd(), "user_data.xlsx")

# Создание Excel-файла, если он отсутствует
if not os.path.exists(EXCEL_FILE):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append([
        "Имя", "Почта", "Реалистичный", "Исследовательский",
        "Артистический", "Социальный", "Предприимчивый",
        "Конвенциональный", "MBTI", "Профессии"
    ])
    wb.save(EXCEL_FILE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test', methods=['POST'])
def process_test():
    try:
        data = request.json
        print("Полученные данные от клиента:", data)

        user = data.get('user')
        answers = data.get('answers')

        if not user or not answers:
            return jsonify({"error": "User data or answers missing"}), 400

        # Категории RIASEC и MBTI
        r_categories = {"Realistic": 0, "Investigative": 0, "Artistic": 0, "Social": 0, "Enterprising": 0, "Conventional": 0}
        mbti_categories = {"Extroversion": 0, "Introversion": 0, "Sensing": 0, "Intuition": 0, "Thinking": 0, "Feeling": 0, "Judging": 0, "Perceiving": 0}

        # Подсчёт результатов
        for answer in answers:
            if answer['category'] in r_categories:
                r_categories[answer['category']] += answer['score']
            elif answer['category'] in mbti_categories:
                mbti_categories[answer['category']] += answer['score']

        # Формирование типа MBTI
        mbti_results = {
            "Extroversion/Introversion": "E" if mbti_categories["Extroversion"] > mbti_categories["Introversion"] else "I",
            "Sensing/Intuition": "S" if mbti_categories["Sensing"] > mbti_categories["Intuition"] else "N",
            "Thinking/Feeling": "T" if mbti_categories["Thinking"] > mbti_categories["Feeling"] else "F",
            "Judging/Perceiving": "J" if mbti_categories["Judging"] > mbti_categories["Perceiving"] else "P"
        }
        mbti_type = "".join([
            mbti_results["Extroversion/Introversion"],
            mbti_results["Sensing/Intuition"],
            mbti_results["Thinking/Feeling"],
            mbti_results["Judging/Perceiving"]
        ])

        # Координаты для графика
        x_axis = (mbti_categories["Intuition"] - mbti_categories["Sensing"]) / 10  # Нормализация
        y_axis = (mbti_categories["Extroversion"] - mbti_categories["Introversion"]) / 10

        # Анализ результатов
        recommendations = analyze_results(r_categories, mbti_type)

        # Сохранение в Excel
        wb = openpyxl.load_workbook(EXCEL_FILE)
        sheet = wb.active
        sheet.append([
            user['name'], user['email'],
            r_categories["Realistic"], r_categories["Investigative"],
            r_categories["Artistic"], r_categories["Social"],
            r_categories["Enterprising"], r_categories["Conventional"],
            mbti_type, ", ".join(recommendations["MBTI_Professions"])
        ])
        wb.save(EXCEL_FILE)

        # Отправка письма
        try:
            msg = Message(
                subject="Результаты теста",
                sender=app.config['MAIL_USERNAME'],
                recipients=[user['email']],
                body=f"""
                Здравствуйте, {user['name']}!

                Ваши результаты теста:
                RIASEC:
                Реалистичный: {r_categories['Realistic']}
                Исследовательский: {r_categories['Investigative']}
                Артистический: {r_categories['Artistic']}
                Социальный: {r_categories['Social']}
                Предприимчивый: {r_categories['Enterprising']}
                Конвенциональный: {r_categories['Conventional']}

                Реалистичный: — Предпочитают практическую работу, такую как инженерия или механика.
                Исследовательский: — Ориентированы на исследование, аналитику и решение сложных задач.
                Артистический: — Творческая личность, подходящая для искусства, дизайна или писательства.
                Социальный: — Любят помогать другим и работать в социальной сфере.
                Предприимчивый: — Обладают лидерскими качествами и подходите для управления и бизнеса.
                Конвенциональный: — Предпочитают организованность и точность, такие как работа с данными.

                MBTI тип личности: {mbti_type}
                Рекомендации: {", ".join(recommendations['MBTI_Professions'])}
                """
            )
            mail.send(msg)
            print(f"Результаты отправлены на {user['email']}")
        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")

        # Ответ API
        return jsonify({
            "RIASEC": [{"category": k, "score": v, "description": recommendations["RIASEC_Descriptions"].get(k, "")} for k, v in r_categories.items()],
            "MBTI": {
                "type": mbti_type,
                "description": recommendations["MBTI_Analysis"],
                "axes": {"x": x_axis, "y": y_axis}
            },
            "Recommendations": {
                "RIASEC_Analysis": recommendations["RIASEC_Analysis"],
                "MBTI_Analysis": recommendations["MBTI_Analysis"],
                "MBTI_Professions": recommendations["MBTI_Professions"]
            }
        })

    except Exception as e:
        print("Ошибка на сервере:", str(e))
        return jsonify({"error": "Server error"}), 500

def analyze_results(r_categories, mbti_type):
    """Генерация анализа на основе RIASEC и MBTI"""
    
    # Описание категорий RIASEC
    r_analysis = {
        "Realistic": "Реалистичный: Предпочитаете практическую работу, такую как инженерия или механика.",
        "Investigative": "Исследовательский: Ориентированы на исследование, аналитику и решение сложных задач.",
        "Artistic": "Артистический: Творческая личность, подходящая для искусства, дизайна или писательства.",
        "Social": "Социальный: Любите помогать другим и работать в социальной сфере.",
        "Enterprising": "Предприимчивый: Обладаете лидерскими качествами и подходите для управления и бизнеса.",
        "Conventional": "Конвенциональный: Предпочитаете организованность и точность, такие как работа с данными."
    }

    # Получение рекомендаций по MBTI
    mbti_professions = mbti_analysis.get(mbti_type, {}).get("professions", [])
    mbti_analysis_desc = mbti_analysis.get(mbti_type, {}).get("description", "Описание не найдено.")

    # Создание анализа RIASEC
    r_analysis_combined = "\n".join([
        f"{category}: {r_analysis[category]}" 
        for category in r_categories if r_categories[category] > 0
    ])

    # Возврат анализа и рекомендаций
    return {
        "RIASEC_Descriptions": r_analysis,  # Все описания категорий RIASEC
        "RIASEC_Analysis": r_analysis_combined,  # Комбинированный анализ для отправки пользователю
        "MBTI_Analysis": mbti_analysis_desc,  # Описание MBTI типа
        "MBTI_Professions": mbti_professions  # Рекомендации по профессиям
    }


if __name__ == '__main__':
    app.run(debug=True)