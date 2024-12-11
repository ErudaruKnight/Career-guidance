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

# Путь к Excel-файлу
EXCEL_FILE = os.path.join(os.getcwd(), "user_data.xlsx")

# Создание Excel-файла, если он отсутствует
if not os.path.exists(EXCEL_FILE):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(["Имя", "Email", "RIASEC", "MBTI", "Результат"])
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
            print("Ошибка: отсутствуют данные пользователя или ответы")
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

        print("Результаты RIASEC:", r_categories)
        print("Результаты MBTI:", mbti_categories)

        # Установить значения по умолчанию для категорий MBTI, если они равны 0
        for key in mbti_categories.keys():
            if mbti_categories[key] == 0:
                mbti_categories[key] = 1

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

        print("Тип MBTI:", mbti_type)

        if not mbti_type or len(mbti_type) != 4:
            print("Ошибка: некорректный тип MBTI")
            mbti_type = "Unknown"

        # Ведущая категория RIASEC
        r_results = sorted(r_categories.items(), key=lambda x: x[1], reverse=True)[:2]

        # Генерация рекомендаций
        recommendations = analyze_results(r_results, mbti_type)
        print("Рекомендации:", recommendations)

        # Сохранение в Excel
        wb = openpyxl.load_workbook(EXCEL_FILE)
        sheet = wb.active
        result_string = f"{recommendations['RIASEC_Analysis']} {recommendations['MBTI_Analysis']}"
        sheet.append([user['name'], user['email'], str(r_results), mbti_type, result_string])
        wb.save(EXCEL_FILE)

        # Отправка email
        send_email(user['email'], r_results, mbti_type, recommendations)

        # Ответ API
        return jsonify({
            "RIASEC": [{"category": k, "score": v} for k, v in r_categories.items()],
            "MBTI": {"type": mbti_type, "description": recommendations["MBTI_Analysis"]},
            "Recommendations": recommendations
        })

    except Exception as e:
        print("Ошибка на сервере:", str(e))
        return jsonify({"error": "Server error"}), 500

def analyze_results(r_results, mbti_type):
    """Генерация анализа на основе RIASEC и MBTI"""
    r_analysis = {
        "Realistic": "Вы предпочитаете практическую работу, связанную с техникой или реальными задачами.",
        "Investigative": "Вы thrive в аналитических и исследовательских ролях, таких как наука, IT или аналитика.",
        "Artistic": "Творческие профессии — ваша сильная сторона. Рассмотрите карьеру в искусстве, дизайне или музыке.",
        "Social": "Вы хорошо справляетесь с помощью другим людям. Подходящие профессии: учитель, консультант.",
        "Enterprising": "Лидерство и бизнес-активности подходят вам. Попробуйте себя в управлении или предпринимательстве.",
        "Conventional": "Вы отлично работаете с данными и системами. Рассмотрите карьеру в бухгалтерии или администрировании."
    }

    mbti_analysis = {
        "INTJ": "Стратег: Стратегические мыслители с воображением и планом на всё.",
        "INTP": "Учёный: Изобретательные и творческие личности, ориентированные на знания.",
        "ENTJ": "Командир: Лидеры с сильным характером, всегда находят путь или создают его.",
        "ENTP": "Полемист: Умные и любопытные мыслители, которые любят интеллектуальные вызовы.",
        "INFJ": "Активист: Идеалисты, вдохновляющие и готовые бороться за свои принципы.",
        "INFP": "Посредник: Поэтичные, добрые и альтруистичные личности, готовые помочь.",
        "ENFJ": "Тренер: Харизматичные лидеры, вдохновляющие и мотивирующие.",
        "ENFP": "Борец: Энтузиасты, общительные и творческие личности с оптимистичным взглядом на жизнь.",
        "ISTJ": "Администратор: Практичные и надёжные люди, на которых можно положиться.",
        "ISFJ": "Защитник: Ответственные и заботливые, защищают своих близких.",
        "ESTJ": "Менеджер: Организаторы, которые превосходно управляют процессами.",
        "ESFJ": "Консул: Заботливые и популярные люди, всегда готовые помочь.",
        "ISTP": "Виртуоз: Экспериментаторы, мастера в работе с инструментами.",
        "ISFP": "Артист: Гибкие и очаровательные личности, всегда ищущие новое.",
        "ESTP": "Делец: Энергичные и сообразительные люди, наслаждающиеся риском.",
        "ESFP": "Развлекатель: Спонтанные и энергичные личности, создающие атмосферу веселья."
    }

    r_top_category = r_results[0][0]
    return {
        "RIASEC_Analysis": r_analysis.get(r_top_category, "Описание отсутствует."),
        "MBTI_Analysis": mbti_analysis.get(mbti_type, "Описание для этого типа отсутствует."),
        "Combined": f"{r_analysis.get(r_top_category, 'Описание отсутствует.')} {mbti_analysis.get(mbti_type, 'Описание отсутствует.')}"
    }

def send_email(email, r_results, mbti_type, recommendations):
    """Отправка email с результатами"""
    msg = Message("Результаты теста профориентации",
                  sender="krosspsih@gmail.com",
                  recipients=[email])
    msg.body = f"""
    Здравствуйте!

    Ваши результаты:
    - RIASEC: {', '.join([f'{cat}: {score}' for cat, score in r_results])}
    - MBTI: {mbti_type}
    - Рекомендации: {recommendations["Combined"]}

    Спасибо за прохождение теста!
    """
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
