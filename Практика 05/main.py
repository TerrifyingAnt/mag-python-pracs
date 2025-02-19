from cool_window import QtWidgets, MainWindow
import os

os.environ['QT_PLUGIN_PATH'] = '.venv\Lib\site-packages\PyQt5\Qt5\plugins'

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())