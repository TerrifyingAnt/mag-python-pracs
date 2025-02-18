from cool_window import QtWidgets, MainWindow
import os

os.environ['QT_PLUGIN_PATH'] = '.venv\Lib\site-packages\PyQt5\Qt5\plugins'

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Пример использования методов для установки текста
    window.set_address("shendyapinartyom@yandex.ru")
    window.set_header("Практическая работа 2")
    window.set_message("ИКМО-01-24, практика №2, скучно...")

    sys.exit(app.exec_())