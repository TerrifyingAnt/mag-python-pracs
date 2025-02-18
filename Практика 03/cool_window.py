from PyQt5 import QtWidgets, uic
import smtplib
import os
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PyQt5.QtWidgets import QFileDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Загружаем UI из файла
        uic.loadUi('main.ui', self)

        # Инициализация виджетов
        self.msg_header = self.findChild(QtWidgets.QTextEdit, 'msg_header')  # Тема
        self.msg_text = self.findChild(QtWidgets.QPlainTextEdit, 'msg_text')  # Текст сообщения
        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')  # Кнопка "Отправить"
        self.server_type = self.findChild(QtWidgets.QComboBox, 'server_type')  # Выбор сервера
        self.msg_addr_from = self.findChild(QtWidgets.QTextEdit, 'msg_addr_from')  # Адрес отправителя
        self.from_password = self.findChild(QtWidgets.QLineEdit, 'from_password')  # Пароль отправителя (QLineEdit)
        self.push_button_choose_files = self.findChild(QtWidgets.QPushButton, 'push_button_choose_files')  # Кнопка выбора CSV-файла

        # Настройка поля для пароля
        self.from_password.setEchoMode(QtWidgets.QLineEdit.Password)  # Отображение пароля как звездочек

        # Привязка событий
        self.pushButton.clicked.connect(self.on_send_button_clicked)
        self.push_button_choose_files.clicked.connect(self.on_choose_csv_file_clicked)

        # Путь к выбранному CSV-файлу
        self.csv_file_path = None

    def set_address(self, text):
        """Установить текст в поле адреса получателя."""
        self.msg_addr_from.setText(text)

    def set_header(self, text):
        """Установить текст в поле темы."""
        self.msg_header.setText(text)

    def set_message(self, text):
        """Установить текст в поле текста сообщения."""
        self.msg_text.setPlainText(text)

    def get_header(self):
        """Получить текст из поля темы."""
        return self.msg_header.toPlainText()

    def get_message(self):
        """Получить текст из поля текста сообщения."""
        return self.msg_text.toPlainText()

    def on_choose_csv_file_clicked(self):
        """Обработчик нажатия на кнопку 'Выбрать CSV-файл'."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите CSV-файл", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            self.csv_file_path = file_path
            QtWidgets.QMessageBox.information(self, "Файл выбран", f"Выбран CSV-файл: {file_path}")

    def on_send_button_clicked(self):
        """Обработчик нажатия на кнопку 'Отправить'."""
        if not self.csv_file_path:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сначала выберите CSV-файл!")
            return

        addr_from = self.msg_addr_from.toPlainText()
        password = self.from_password.text()  # Получаем пароль из QLineEdit
        msg_subj = self.get_header()
        msg_text = self.get_message()

        if not addr_from or not password or not msg_subj or not msg_text:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        server_type = self.server_type.currentText()
        smtp_server, smtp_port = self.get_smtp_settings(server_type)

        try:
            # Чтение данных из CSV-файла
            recipients_data = self.read_csv_file(self.csv_file_path)

            # Отправка писем каждому получателю
            for recipient_email, attachments in recipients_data:
                send_email(addr_from, password, recipient_email, msg_subj, msg_text, attachments, smtp_server, smtp_port)

            QtWidgets.QMessageBox.information(self, "Успех", "Все письма успешно отправлены!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось отправить письма: {str(e)}")

    def read_csv_file(self, file_path):
        """Чтение данных из CSV-файла."""
        recipients_data = []
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            for row in reader:
                if len(row) < 2:
                    continue  # Пропускаем некорректные строки
                recipient_email = row[0].strip()
                attachments = [attachment.strip() for attachment in row[1:] if attachment.strip()]
                recipients_data.append((recipient_email, attachments))
        return recipients_data

    def get_smtp_settings(self, server_type):
        """Получить настройки SMTP-сервера."""
        if server_type == "yandex":
            return "smtp.yandex.ru", 587
        elif server_type == "mail":
            return "smtp.mail.ru", 587
        elif server_type == "gmail":
            return "smtp.gmail.com", 587
        else:
            raise ValueError("Неизвестный тип сервера")


def send_email(addr_from, password, addr_to, msg_subj, msg_text, attachments, smtp_server, smtp_port):
    """Отправка электронного письма с вложениями."""
    # Создаем multipart-сообщение
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = addr_to
    msg['Subject'] = msg_subj

    # Добавляем текстовое содержимое
    msg.attach(MIMEText(msg_text, 'plain'))

    # Добавление вложений
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
            print(f"Не удалось прикрепить файл {file_path}: {str(e)}")

    # Подключение к SMTP-серверу
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(addr_from, password)
        server.sendmail(addr_from, [addr_to], msg.as_string())
        server.quit()
    except Exception as e:
        raise RuntimeError(f"Ошибка при отправке письма: {str(e)}")


