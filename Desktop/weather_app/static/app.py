from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(_name_)

API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    alerts = []

    if request.method == "POST":
        city = request.form["city"]
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            weather_data = data

            for item in data["list"][:8]:  # Next 24 hours (3-hour intervals)
                temp = item['main']['temp']
                rain = item.get('rain', {}).get('3h', 0)
                dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
                alert_msg = f"{dt.strftime('%d %b %I:%M %p')} - Temp: {temp}°C, Rain: {rain}mm"
                if temp > 35:
                    alert_msg += " ⚠️ High Temp!"
                if rain > 0:
                    alert_msg += " 🌧️ Rain Expected"
                alerts.append(alert_msg)

    return render_template("index.html", weather_data=weather_data, alerts=alerts)

if _name_ == "_main_":
    app.run(debug=True)