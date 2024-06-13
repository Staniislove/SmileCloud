import requests

class WeatherApi:
    def __init__(self):
        self.api_key = "036950c45dcd417d392bcf0ebbbbe1cc"  # ключ OpenWeatherApi

    def get_weather_data(self, city):
        """Запрашивает данные погоды с API и возвращает их"""
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        )
        response.raise_for_status()
        data = response.json()
        # Извлекаем данные из ответа
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]
        return temperature, description, wind_speed, humidity