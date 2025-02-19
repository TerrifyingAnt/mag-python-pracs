from cool_window import QtWidgets, DatabaseApp
import os
import sys

os.environ['QT_PLUGIN_PATH'] = '.venv\Lib\site-packages\PyQt5\Qt5\plugins'

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = DatabaseApp()
    window.show()

    sys.exit(app.exec_())