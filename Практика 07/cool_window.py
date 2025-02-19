import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class DatabaseApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(DatabaseApp, self).__init__()

        # Загрузка интерфейса из XML (.ui файла)
        uic.loadUi("main.ui", self)

        # Подключение к PostgreSQL через SQLAlchemy
        self.engine = None
        self.session = None
        self.current_database = None
        self.current_table = None

        # Подключение сигналов к слотам
        #self.getTablesFromChosenDatabaseBUTTON.clicked.connect(self.load_tables)
        self.executeRequestBUTTON.clicked.connect(self.execute_sql_request)
        self.createTableBUTTON.clicked.connect(self.create_table)
        self.deleteTableBUTTON.clicked.connect(self.delete_table)
        self.addNewFieldInTableBUTTON.clicked.connect(self.add_field_to_create_table_widget)
        self.deleteChosenFieldFromTableBUTTON.clicked.connect(self.delete_field_from_create_table_widget)
        self.addValueToChosenTableBUTTON.clicked.connect(self.add_value_to_add_values_widget)
        self.deleteValueFromChosenTableBUTTON.clicked.connect(self.delete_value_from_add_values_widget)

        self.executeAddingValuesBUTTON.clicked.connect(self.insert_values)

        # Добавляем обработчик для кнопки "Просмотреть"
        self.getTablesFromChosenDatabaseBUTTON.clicked.connect(self.view_table_data)

        # Загрузка списка баз данных
        self.load_databases()

    def connect_to_database(self, database=None):
        """Подключение к PostgreSQL через SQLAlchemy"""
        try:
            if self.engine:
                self.engine.dispose()
            connection_string = f"postgresql+psycopg2://postgres:postgres@localhost:6543/ch_postgres_db"
            self.engine = create_engine(connection_string)
            self.session = sessionmaker(bind=self.engine)()
            return True
        except SQLAlchemyError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к базе данных:\n{str(e)}")
            return False

    def load_databases(self):
        """Загрузка списка баз данных"""
        if self.connect_to_database():
            try:
                #inspector = inspect(self.engine)
                databases = [self.engine.url.database]
                self.comboBoxDatabases.clear()
                self.comboBoxDatabases.addItems(databases)
                self.load_tables()
            except SQLAlchemyError as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список баз данных:\n{str(e)}")

    def load_tables(self):
        """Загрузка списка таблиц для выбранной базы данных"""
        self.current_database = self.comboBoxDatabases.currentText()
        if self.connect_to_database(self.current_database):
            try:
                inspector = inspect(self.engine)
                tables = inspector.get_table_names(schema="public")
                self.comboBoxTables.clear()
                self.comboBoxTables.addItems(tables)
            except SQLAlchemyError as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список таблиц:\n{str(e)}")

    def execute_sql_request(self):
        """Выполнение SQL-запроса"""
        query = self.sqlRequest.text()
        if not query.strip():
            QMessageBox.warning(self, "Ошибка", "SQL-запрос пуст!")
            return

        if self.connect_to_database(self.current_database):
            try:
                result = self.session.execute(text(query))
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    result_text = "\t".join(columns) + "\n"
                    for row in rows:
                        result_text += "\t".join(map(str, row)) + "\n"
                    self.showData.setPlainText(result_text)
                else:
                    self.showData.setPlainText("Запрос выполнен успешно.")
                self.session.commit()
            except SQLAlchemyError as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить запрос:\n{str(e)}")
                self.session.rollback()

    def view_table_data(self):
        """Просмотр данных из выбранной таблицы"""
        table_name = self.comboBoxTables.currentText()
        if not table_name:
            QMessageBox.warning(self, "Ошибка", "Таблица не выбрана!")
            return

        if self.connect_to_database(self.current_database):
            try:
                query = text(f"SELECT * FROM {table_name};")
                with self.engine.connect() as conn:
                    result = conn.execute(query)
                    if result.returns_rows:
                        columns = result.keys()
                        rows = result.fetchall()
                        result_text = "\t".join(columns) + "\n"
                        for row in rows:
                            result_text += "\t".join(map(str, row)) + "\n"
                        self.showData.setPlainText(result_text)
                    else:
                        self.showData.setPlainText("Таблица пуста.")
            except SQLAlchemyError as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные из таблицы:\n{str(e)}")

    def add_field_to_create_table_widget(self):
        """Добавление новой строки в виджет для создания таблицы"""
        row_position = self.createTableWidget.rowCount()
        self.createTableWidget.insertRow(row_position)

    def delete_field_from_create_table_widget(self):
        """Удаление строки из виджета для создания таблицы"""
        current_row = self.createTableWidget.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Нет выбранной строки для удаления!")
            return
        self.createTableWidget.removeRow(current_row)

    def create_table(self):
        """Создание новой таблицы"""
        table_name = self.createTableWidget.item(0, 0).text() if self.createTableWidget.rowCount() > 0 else None
        if not table_name:
            QMessageBox.warning(self, "Ошибка", "Имя таблицы не указано!")
            return

        metadata = MetaData()
        columns = []
        for row in range(self.createTableWidget.rowCount()):
            field_name = self.createTableWidget.item(row, 0).text()
            field_type = self.createTableWidget.item(row, 1).text()
            if field_name and field_type:
                if field_type.lower() == "integer":
                    columns.append(Column(field_name, Integer))
                elif field_type.lower() == "string":
                    columns.append(Column(field_name, String))

        if not columns:
            QMessageBox.warning(self, "Ошибка", "Нет полей для создания таблицы!")
            return

        try:
            new_table = Table(table_name, MetaData(), *columns)
            new_table.create(self.engine)
            QMessageBox.information(self, "Успех", "Таблица создана успешно!")
            self.load_tables()
        except SQLAlchemyError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать таблицу:\n{str(e)}")

    def delete_table(self):
        """Удаление таблицы"""
        table_name = self.comboBoxTables.currentText()
        if not table_name:
            QMessageBox.warning(self, "Ошибка", "Таблица не выбрана!")
            return

        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=self.engine)
            table.drop(self.engine)
            QMessageBox.information(self, "Успех", "Таблица удалена успешно!")
            self.load_tables()
        except SQLAlchemyError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить таблицу:\n{str(e)}")

    def add_value_to_add_values_widget(self):
        """Добавление новой строки в виджет для добавления значений"""
        row_position = self.addValuesWidget.rowCount()
        self.addValuesWidget.insertRow(row_position)

    def delete_value_from_add_values_widget(self):
        """Удаление строки из виджета для добавления значений"""
        current_row = self.addValuesWidget.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Нет выбранной строки для удаления!")
            return
        self.addValuesWidget.removeRow(current_row)

    def insert_values(self):
        """Вставка значений в таблицу"""
        table_name = self.comboBoxTables.currentText()
        if not table_name:
            QMessageBox.warning(self, "Ошибка", "Таблица не выбрана!")
            return

        columns = []
        values = []
        for row in range(self.addValuesWidget.rowCount()):
            column_name = self.addValuesWidget.item(row, 0).text()
            value = self.addValuesWidget.item(row, 1).text()
            if column_name and value:
                columns.append(column_name)
                values.append(f"'{value}'")  # Значения оборачиваются в кавычки

        if not columns or not values:
            QMessageBox.warning(self, "Ошибка", "Нет значений для вставки!")
            return

        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
        try:
            with self.engine.connect() as conn:
                conn.execute(text(query))  # Используем text для корректного выполнения запроса
                conn.commit()  # Фиксируем транзакцию
            QMessageBox.information(self, "Успех", "Значения вставлены успешно!")
            self.view_table_data()  # Обновляем данные в интерфейсе
        except SQLAlchemyError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось вставить значения:\n{str(e)}")
