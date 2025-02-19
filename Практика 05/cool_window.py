from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

def safe_eval(expression):
    try:
        allowed_names = {
            'abs': abs,
            'pow': pow,
            'round': round
        }
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Ошибка: {str(e)}"

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi("main.ui", self)  
        self.pushButton.clicked.connect(self.calculate)

    def calculate(self):
        expression = self.lineEdit.text()

        # Проверяем, что поле не пустое
        if not expression.strip():
            self.label_2.setText("Результат: ")
            QMessageBox.warning(self, "Ошибка", "Поле ввода пустое!")
            return

        result = safe_eval(expression)
        self.label_2.setText(f"Результат: {result}")
