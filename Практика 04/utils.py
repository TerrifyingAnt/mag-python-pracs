import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(addr_from, password, addr_to, msg_subj, msg_text, attachments, smtp_server, smtp_port):
    """Отправка электронного письма с возможными вложениями."""
    # Создаем multipart-сообщение
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = addr_to
    msg['Subject'] = msg_subj

    # Добавляем текстовое содержимое
    msg.attach(MIMEText(msg_text, 'plain'))

    # Добавление вложений (если они есть)
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                    mime_part = MIMEBase("application", "octet-stream")
                    mime_part.set_payload(file_data)
                    encoders.encode_base64(mime_part)
                    mime_part.add_header("Content-Disposition", f"attachment; filename={file_name}")
                    msg.attach(mime_part)
            except Exception as e:
                return f"Не удалось прикрепить файл {file_path}: {str(e)}"

    # Подключение к SMTP-серверу
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(addr_from, password)
        server.sendmail(addr_from, [addr_to], msg.as_string())
        server.quit()
        return "Письмо успешно отправлено!"
    except Exception as e:
        return f"Ошибка при отправке письма: {str(e)}"