import sqlite3 as sl

if __name__ == '__main__':
    con = sl.connect('relay_protection.db')
    with con:
        con.execute("""
            CREATE TABLE SIGNALS (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                time INTEGER,
                signal_0 INTEGER,
                signal_1 INTEGER,
                signal_2 INTEGER,
                signal_3 INTEGER,
                signal_4 INTEGER,
                signal_5 INTEGER,
                signal_6 INTEGER,
                signal_7 INTEGER,
                signal_8 INTEGER,
                signal_9 INTEGER,
                signal_10 INTEGER,
                signal_11 INTEGER
            );
        """)


class Database:
    """
        Класс для взаимодействия с SQLite Database
    """

    def __init__(self, signals: object):
        """
        :param signals: Объект класса Signals по которому строится табличка и заполняются данные в БД
        """
        self.signals = signals
        self.conn = sl.connect('relay_protection.db')
        self.columns = [x for x in self.signals.__dict__.keys() if any(substring in x for substring in ('rms', 'time'))]

    def add_signals_table(self):
        """
        Метод для создания таблицы сигналов
        """
        table_create_query = "CREATE TABLE IF NOT EXISTS signals (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
        for i in range(len(self.columns)):
            if self.columns[i] == 'time':
                table_create_query += self.columns[i] + " INTEGER"
            else:
                table_create_query += self.columns[i] + " REAL"
            if i != len(self.columns) - 1:
                table_create_query += ","
        table_create_query += ");"
        with self.conn:
            self.conn.execute(table_create_query)

    def add_row(self, data: list):
        """
        Функция для добавление кортежа в таблицу signals
        :param data: кортеж с измерениями
        """
        insert_query = f"INSERT INTO signals({'id,' + ','.join(self.columns)}) values ({','.join('?' for _ in range(len(self.columns) + 1))})"
        with self.conn:
            self.conn.execute(insert_query, data)
