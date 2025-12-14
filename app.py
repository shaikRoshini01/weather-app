from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv
import os

API_KEY=os.environ.get("API_KEY")
print("API KEY from .env:",API_KEY)

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    current_weather = None
    alerts = []
    city=""
    current_time = datetime.now().strftime("%d %b %Y - %I:%M %p")
    if request.method == "POST":
        city = request.form["city"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city()}&appid={API_KEY}"

        try:
            response = requests.get(url)
            data = response.json()
            if 'list' not in data:
                return render_template("index.html", error=f"City '{city}' not found!")

            weather_data = data

            # Forecast data lists
            dates = [datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S") for item in data['list']]
            temps = [item['main']['temp'] for item in data['list']]
            humidity = [item['main']['humidity'] for item in data['list']]
            wind = [item['wind']['speed'] for item in data['list']]
            rain = [item.get('rain', {}).get('3h', 0) for item in data['list']]

            #  Generate alerts
            for i, item in enumerate(data["list"][:8]):
                dt = dates[i].strftime("%d %b %I:%M %p")
                temp = temps[i]
                r = rain[i]
                alert = f"{dt} - Temp: {temp}°C, Rain: {r}mm"
                if temp >= 35:
                    alert += " ⚠️ High Temp!"
                if r > 0:
                    alert += " 🌧️ Rain Expected"
                if "⚠️" in alert or "🌧️" in alert:
                    alerts.append(alert)

            #  Create plot
            plt.figure(figsize=(12, 6))
            plt.plot(dates, temps, label="Temp (°C)", color="tomato", marker="o")
            plt.plot(dates, humidity, label="Humidity (%)", color="dodgerblue", marker="x")
            plt.plot(dates, wind, label="Wind (m/s)", color="green", marker="^")
            plt.plot(dates, rain, label="Rain (mm)", color="purple", marker="s")
            plt.xticks(rotation=45)
            plt.xlabel("Date & Time")
            plt.ylabel("Values")
            plt.title(f"5-Day Forecast for {city}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            if not os.path.exists("static"):
                os.makedirs("static")
            plt.savefig("static/forecast.png")
            plt.close()

        except Exception as e:
            return render_template("index.html", error=str(e),current_time=current_time)
    return render_template("index.html",city=city, weather_data=weather_data,current_weather=current_weather, alerts=alerts, current_time=current_time)
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=int(os.environ.get("PORT",5000)))