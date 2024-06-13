import sqlite3

class WeatherDatabase:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.create_table()

    def create_table(self):
        """Создает таблицу в бд"""
        cursor = self.db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                temperature REAL,
                description TEXT,
                wind_speed REAL,
                humidity INTEGER
            )
        """)
        self.db_conn.commit()

    def save_weather_data(self, city, temperature, description, wind_speed, humidity):
        """Сохраняет данные погоды в базу данных"""
        cursor = self.db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO weather_history (city, temperature, description, wind_speed, humidity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (city, temperature, description, wind_speed, humidity),
        )
        self.db_conn.commit()

    def get_weather_history(self):
        """Возвращает историю запросов"""
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM weather_history")
        return cursor.fetchall()

    def update_history_entry(self, new_data):
        """Обновляет запись в базе данных"""
        query = """
        UPDATE weather_history
        SET city=?, temperature=?, description=?, wind_speed=?, humidity=?
        WHERE id=?
        """
        cursor = self.db_conn.cursor()
        cursor.execute(query, (new_data[1], new_data[2], new_data[3], new_data[4], new_data[5], new_data[0]))
        self.db_conn.commit()

    def change_history_entry(self, id):
        cursor = self.db_conn.cursor()
        cursor.execute("DELETE FROM Weather WHERE ID=?", (id,))
        self.db_conn.commit()

    def delete_history_entry(self, entry_id):
        """Удаляет запись в базе данных"""
        query = "DELETE FROM weather_history WHERE id=?"
        cursor = self.db_conn.cursor()
        cursor.execute(query, (entry_id,))
        self.db_conn.commit()


    def close_connection(self):
        """Закрывает соединение с базой данных"""
        self.db_conn.close()