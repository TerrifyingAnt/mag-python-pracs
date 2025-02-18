from PyQt5 import QtWidgets, uic
import smtplib

import os
from dotenv import load_dotenv 

from email.message import EmailMessage

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Загружаем UI из файла
        uic.loadUi('main.ui', self)

        # Инициализация виджетов
        self.msg_addr = self.findChild(QtWidgets.QTextEdit, 'msg_addr')
        self.msg_header = self.findChild(QtWidgets.QTextEdit, 'msg_header')
        self.msg_text = self.findChild(QtWidgets.QPlainTextEdit, 'msg_text')
        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')

        self.pushButton.clicked.connect(self.on_send_button_clicked)

    def set_address(self, text):
        self.msg_addr.setText(text)

    def set_header(self, text):
        self.msg_header.setText(text)

    def set_message(self, text):
        self.msg_text.setPlainText(text)

    def get_address(self):
        return self.msg_addr.toPlainText()

    def get_header(self):
        return self.msg_header.toPlainText()

    def get_message(self):
        return self.msg_text.toPlainText()

    def on_send_button_clicked(self):
        address = self.get_address()
        header = self.get_header()
        message = self.get_message()
        print(f"Адрес: {address}")
        print(f"Тема: {header}")
        print(f"Сообщение: {message}")
        send_email(address, header, message)
        


def send_email(addr_to, msg_subj, msg_text): 
    load_dotenv() 
    msg = EmailMessage()
    msg['From'] = os.getenv("LOGIN")
    msg['To'] = addr_to 
    msg['Subject'] = msg_subj
    msg.set_content(msg_text) 
    try:
        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(os.getenv("LOGIN"), os.getenv("PASSWORD"))
        server.set_debuglevel(1)
        server.sendmail(os.getenv("LOGIN"), [addr_to], msg.as_string())
        server.quit() 
    except Exception as e:
        raise RuntimeError(f"Ошибка при отправке письма: {str(e)}")
