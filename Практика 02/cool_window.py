from PyQt5 import QtWidgets, uic
import smtplib
import os
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
        self.msg_addr = self.findChild(QtWidgets.QTextEdit, 'msg_addr')  # Адрес получателя
        self.msg_header = self.findChild(QtWidgets.QTextEdit, 'msg_header')  # Тема
        self.msg_text = self.findChild(QtWidgets.QPlainTextEdit, 'msg_text')  # Текст сообщения
        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')  # Кнопка "Отправить"
        self.server_type = self.findChild(QtWidgets.QComboBox, 'server_type')  # Выбор сервера
        self.msg_addr_from = self.findChild(QtWidgets.QTextEdit, 'msg_addr_from')  # Адрес отправителя
        self.from_password = self.findChild(QtWidgets.QLineEdit, 'from_password')  # Пароль отправителя (QLineEdit)
        self.push_button_choose_files = self.findChild(QtWidgets.QPushButton, 'push_button_choose_files')  # Кнопка выбора файлов
        self.msg_header_2 = self.findChild(QtWidgets.QTextEdit, 'msg_header_2')  # Поле для отображения выбранных файлов

        # Настройка поля для пароля
        self.from_password.setEchoMode(QtWidgets.QLineEdit.Password)  # Отображение пароля как звездочек

        # Привязка событий
        self.pushButton.clicked.connect(self.on_send_button_clicked)
        self.push_button_choose_files.clicked.connect(self.on_choose_files_clicked)

        # Список выбранных файлов
        self.selected_files = []

    def set_address(self, text):
        """Установить текст в поле адреса получателя."""
        self.msg_addr.setText(text)

    def set_header(self, text):
        """Установить текст в поле темы."""
        self.msg_header.setText(text)

    def set_message(self, text):
        """Установить текст в поле текста сообщения."""
        self.msg_text.setPlainText(text)

    def get_address(self):
        """Получить текст из поля адреса получателя."""
        return self.msg_addr.toPlainText()

    def get_header(self):
        """Получить текст из поля темы."""
        return self.msg_header.toPlainText()

    def get_message(self):
        """Получить текст из поля текста сообщения."""
        return self.msg_text.toPlainText()

    def on_choose_files_clicked(self):
        """Обработчик нажатия на кнопку 'Выбрать файл'."""
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы", "", "All Files (*);;", options=options)
        if files:
            self.selected_files = files
            self.msg_header_2.setText("\n".join(files))  # Отображаем список выбранных файлов

    def on_send_button_clicked(self):
        """Обработчик нажатия на кнопку 'Отправить'."""
        addr_to = self.get_address()
        addr_from = self.msg_addr_from.toPlainText()
        password = self.from_password.text()  # Получаем пароль из QLineEdit
        msg_subj = self.get_header()
        msg_text = self.get_message()

        if not addr_to or not addr_from or not password or not msg_subj or not msg_text:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        server_type = self.server_type.currentText()
        smtp_server, smtp_port = self.get_smtp_settings(server_type)

        try:
            send_email(addr_from, password, addr_to, msg_subj, msg_text, self.selected_files, smtp_server, smtp_port)
            QtWidgets.QMessageBox.information(self, "Успех", "Письмо успешно отправлено!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось отправить письмо: {str(e)}")

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

