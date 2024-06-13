import sys
import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, \
                            QPushButton, QMessageBox, \
                            QDialog, QGridLayout, QWidget

from weather_ui import Ui_Form  # модуль с UI-интерфейсом
from edid_dialog import EditDialog  # модуль с окном изменения БД
import weather_api  # модуль с API
import weather_db  # модуль с базой данных


class WeatherApp(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Инициализируйте UI из Qt Designer

        self.setWindowTitle("Smile cloud")
        self.setWindowIcon(QIcon('images/cloud.png'))

        # API
        self.weather_api = weather_api.WeatherApi()  # Создаем объект API

        # База данных
        self.db_conn = sqlite3.connect("weather_data.db")
        self.db = weather_db.WeatherDatabase(self.db_conn)  # Создаем объект базы данных

        # Сигналы
        self.get_weather_button.clicked.connect(self.get_weather)
        self.history_button.clicked.connect(self.show_history)

        # Drag & Drop
        self.gif_label.setAcceptDrops(True)
        self.gif_label.installEventFilter(self)
        gif = QMovie("images/tudasuda.gif")
        self.gif_label.setMovie(gif)
        gif.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos() - self.gif_label.pos()  # Сохранить начальную позицию мыши относительно gif_label

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_position = event.pos() - self.drag_start_position
            self.gif_label.move(new_position)  # Обновить позицию gif_label в соответствии с перемещением мыши

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0].toLocalFile()
        if url.lower().endswith("images/tudasuda.gif"):
            self.gif_label.setPixmap(QPixmap(url))
            event.acceptProposedAction()

    def get_weather(self):
        """Запрашивает данные погоды с API и отображает их"""
        city = self.city_input.text()
        if city:
            try:
                temperature, description, wind_speed, humidity = self.weather_api.get_weather_data(city)
                self.set_weather_info(temperature, description, wind_speed, humidity)

                # Сохраняем в бд
                self.db.save_weather_data(city, temperature, description, wind_speed, humidity)

            except Exception as e:  # Обрабатываем исключения из API
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить данные: {e}")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите город.")

    def set_weather_info(self, temperature, description, wind_speed, humidity):
        """Устанавливает информацию о погоде в метку"""
        self.weather_info_label.setText(
            f"Температура: {temperature:.1f}°C\n"
            f"Описание: {description}\n"
            f"Скорость ветра: {wind_speed} м/с\n"
            f"Влажность: {humidity}%"
        )

    def show_history(self):
        """Отображает историю запросов"""
        history = self.db.get_weather_history()
        if history:
            # Проверяем, существует ли уже диалоговое окно истории
            if hasattr(self, 'history_dialog') and self.history_dialog.isVisible():
                self.history_dialog.close()

            # Создаем диалоговое окно для истории
            self.history_dialog = QDialog(self)
            self.history_dialog.setWindowTitle("История запросов")
            history_layout = QGridLayout()

            # Добавляем заголовки столбцов (исключая ID)
            history_layout.addWidget(QLabel("Город"), 0, 0)
            history_layout.addWidget(QLabel("Температура"), 0, 1)
            history_layout.addWidget(QLabel("Описание"), 0, 2)
            history_layout.addWidget(QLabel("Скорость ветра"), 0, 3)
            history_layout.addWidget(QLabel("Влажность"), 0, 4)
            history_layout.addWidget(QLabel("Изменить"), 0, 5)
            history_layout.addWidget(QLabel("Удалить"), 0, 6)

            # Добавляем строки с историей запросов
            row = 1
            for row_data in history:
                # Добавляем город
                city_label = QLabel(row_data[1])
                history_layout.addWidget(city_label, row, 0)

                # Добавляем информацию о погоде
                history_layout.addWidget(QLabel(f"{row_data[2]:.1f}°C"), row, 1)
                history_layout.addWidget(QLabel(row_data[3]), row, 2)
                history_layout.addWidget(QLabel(f"{row_data[4]:.1f} м/с"), row, 3)
                history_layout.addWidget(QLabel(f"{row_data[5]}%"), row, 4)

                # Добавляем кнопку "Изменить"
                change_button = QPushButton("Изменить")
                change_button.clicked.connect(lambda ch, rd=row_data: self.edit_entry(rd))
                history_layout.addWidget(change_button, row, 5)

                # Добавляем кнопку "Удалить"
                delete_button = QPushButton("Удалить")
                delete_button.clicked.connect(lambda del_ch, del_rd=row_data: self.delete_entry(del_rd[0]))
                history_layout.addWidget(delete_button, row, 6)
                row += 1

            self.history_dialog.setLayout(history_layout)
            self.history_dialog.exec_()  # Отображаем диалоговое окно
        else:
            QMessageBox.information(self, "История", "История пуста.")

    def edit_entry(self, row_data):
        """Открывает диалоговое окно для редактирования записи"""
        dialog = EditDialog(self, row_data)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            self.db.update_history_entry(new_data)
            self.show_history()  # Обновляем историю после изменения

    def delete_entry(self, entry_id):
        """Удаляет запись из истории по ID"""
        reply = QMessageBox.question(self, 'Подтверждение удаления',
                                     'Вы уверены, что хотите удалить эту запись?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.delete_history_entry(entry_id)
            self.show_history()  # Обновляем историю после удаления

    def closeEvent(self, event):
        """Закрытие приложения"""
        self.db_conn.close()  # Закрываем соединение с базой данных
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())