from flask import Flask, request, jsonify
from utils import *

app = Flask(__name__)

@app.route('/send-email', methods=['POST'])
def send_email_handler():
    """Обработчик POST-запроса для отправки письма."""
    try:
        # Получаем данные из JSON-тела запроса
        data = request.json
        addr_from = data.get('addr_from')
        password = data.get('password')
        addr_to = data.get('addr_to')
        msg_subj = data.get('msg_subj')
        msg_text = data.get('msg_text')
        attachments = data.get('attachments', [])
        server_type = data.get('server_type')

        # Проверяем обязательные поля
        if not all([addr_from, password, addr_to, msg_subj, msg_text, server_type]):
            return jsonify({"error": "Необходимо заполнить все обязательные поля"}), 400

        # Получаем настройки SMTP-сервера
        if server_type == "yandex":
            smtp_server, smtp_port = "smtp.yandex.ru", 587
        elif server_type == "mail":
            smtp_server, smtp_port = "smtp.mail.ru", 587
        elif server_type == "gmail":
            smtp_server, smtp_port = "smtp.gmail.com", 587
        else:
            return jsonify({"error": "Неизвестный тип сервера"}), 400

        # Отправляем письмо
        result = send_email(addr_from, password, addr_to, msg_subj, msg_text, attachments, smtp_server, smtp_port)
        return jsonify({"message": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/', methods=['GET'])
def base_route_handler():
    return "ПРАКТИКА №4, ИКМО-01-24, Шендяпин Артём, скучно...("


if __name__ == '__main__':
    app.run(debug=True)