from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ.get("API_KEY")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    alerts = []
    city = ""
    current_time = datetime.now().strftime("%d %b %Y - %I:%M %p")

    if request.method == "POST":
        city_name = request.form.get("city")
        city = city_name

        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=metric"

        try:
            response = requests.get(url)

            if response.status_code != 200:
                return render_template(
                    "index.html",
                    error="City not found. Please enter a valid city name.",
                    current_time=current_time
                )

            data = response.json()

            if "list" not in data:
                return render_template(
                    "index.html",
                    error="Forecast data not available.",
                    current_time=current_time
                )

            weather_data = data

            dates = [datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S") for item in data["list"]]
            temps = [item["main"]["temp"] for item in data["list"]]
            humidity = [item["main"]["humidity"] for item in data["list"]]
            wind = [item["wind"]["speed"] for item in data["list"]]
            rain = [item.get("rain", {}).get("3h", 0) for item in data["list"]]

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

            plt.figure(figsize=(12, 6))
            plt.plot(dates, temps, label="Temp (°C)", marker="o")
            plt.plot(dates, humidity, label="Humidity (%)", marker="x")
            plt.plot(dates, wind, label="Wind (m/s)", marker="^")
            plt.plot(dates, rain, label="Rain (mm)", marker="s")
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

        except Exception:
            return render_template(
                "index.html",
                error="Something went wrong. Please try again.",
                current_time=current_time
            )

    return render_template(
        "index.html",
        city=city,
        weather_data=weather_data,
        alerts=alerts,
        current_time=current_time
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))