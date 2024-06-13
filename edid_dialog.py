from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPushButton

class EditDialog(QDialog):
    def __init__(self, parent=None, row_data=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать запись")
        self.row_data = row_data
        self.init_ui()

    def init_ui(self):
        """Создание диалогового окна для изменения данных в истории"""
        layout = QFormLayout()

        self.id_label = QLabel(str(self.row_data[0]))
        self.city_edit = QLineEdit(self.row_data[1])
        self.temp_edit = QLineEdit(str(self.row_data[2]))
        self.desc_edit = QLineEdit(self.row_data[3])
        self.wind_speed_edit = QLineEdit(str(self.row_data[4]))
        self.humidity_edit = QLineEdit(str(self.row_data[5]))

        layout.addRow("ID:", self.id_label)
        layout.addRow("Город:", self.city_edit)
        layout.addRow("Температура:", self.temp_edit)
        layout.addRow("Описание:", self.desc_edit)
        layout.addRow("Скорость ветра:", self.wind_speed_edit)
        layout.addRow("Влажность:", self.humidity_edit)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)

        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def get_data(self):
        return (
            self.id_label.text(),
            self.city_edit.text(),
            float(self.temp_edit.text()),
            self.desc_edit.text(),
            float(self.wind_speed_edit.text()),
            int(self.humidity_edit.text())
        )