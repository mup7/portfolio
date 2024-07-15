from dotenv import load_dotenv
import os
from flask import Flask, render_template, request
import smtplib
import datetime
import random
import requests

# Load environment variables from .env file
load_dotenv()

# smtplib constants
MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASSWORD = os.environ.get("MY_PASSWORD")
# genderize constant
GENDERIZE_API_ENDPOINT = "https://api.genderize.io"
# ageify constant
AGEIFY_API_ENDPOINT = "https://api.agify.io"
# openweathermap constants
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
GEOCODING_API_ENDPOINT = "http://api.openweathermap.org/geo/1.0/direct"
OPENWEATHERMAP_API_ENDPOINT = "http://api.openweathermap.org/data/2.5/forecast"
# nutritionix constants
NUTRITIONIX_APP_ID = os.environ.get("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.environ.get("NUTRITIONIX_API_KEY")
NUTRITIONIX_ENDPOINT = "https://trackapi.nutritionix.com/v2/natural/exercise"
NUTRITIONIX_HEADERS = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY
}

app = Flask(__name__)


def send_email(subject, full_name, email, phone_number, message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()  # Secure the connection
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL, 
            to_addrs=MY_EMAIL, 
            msg=f"Subject: {subject}\n\n"
            f"Full Name: {full_name}\n"
            f"Email: {email}\n"
            f"Phone Number: {phone_number}\n"
            f"Message: {message}"
        )


# Built-in way to inject common variables into the template context for all templates rendered
# context processor is a function that returns a dictionary of variables that will be added to the template context
@app.context_processor
def inject_common_variables():
    current_year = datetime.datetime.now().year
    return {
        'current_year': current_year
        }


@app.route(rule="/")
def home():
    return render_template(template_name_or_list="index.html")


def footer():
    return render_template(template_name_or_list="footer-section.html")


@app.route(rule="/thank-you", methods=["GET", "POST"])
def contact():
    """
    Handles the contact form submission.
    - On POST request: collects form data, sends an email, and renders a thank-you page.
    - On GET request: renders the contact form.
    """
    if request.method == "POST":
        data = request.form
        full_name_input = data["fullName"]
        email_input = data["email"]
        phone_number_input = data["phoneNumber"]
        subject_input = data["subject"]
        message_input = data["message"]

        # Send the email
        send_email(subject=subject_input, full_name=full_name_input, email=email_input, phone_number=phone_number_input, message=message_input)
        return render_template(template_name_or_list="thank-you.html")
    return render_template(template_name_or_list="index.html")


@app.route(rule="/projects")
def projects():
    return render_template(template_name_or_list="projects.html")


# Band Name Generator
@app.route(rule="/projects/band-name-generator", methods=["GET", "POST"])
def band_name_generator():
    """
    Generates a band name based on user input.
    - On POST request: combines city name and pet name to create a band name.
    - On GET request: renders the band name generator form.
    """
    if request.method == "POST":
        data = request.form
        city_name = data["cityName"].title()
        pet_name = data["petName"].title()
        band_name = f"{city_name} {pet_name}"
        return render_template(template_name_or_list="band-name-generator.html", BAND_NAME=band_name)
    return render_template(template_name_or_list="band-name-generator.html")


# Tip Calculator
@app.route(rule="/projects/tip-calculator", methods=["GET", "POST"])
def tip_calculator():
    """
    Calculates the tip per person based on user input.
    - On POST request: calculates the total bill per person and formats it.
    - On GET request: renders the tip calculator form.
    """
    if request.method == "POST":
        try:
            data = request.form
            bill = float(data["bill"])
            tip = float(data["tip"])
            people = int(data["people"])
            tip_as_decimal = tip / 100
            bill_with_tip = bill * (1 + tip_as_decimal)
            bill_per_person = bill_with_tip / people
            bill_per_person_rounded = round(bill_per_person, 2)
            bill_per_person_formatted = f"${bill_per_person_rounded:.2f}"
            return render_template(template_name_or_list="tip-calculator.html", FINAL_BILL_PER_PERSON=bill_per_person_formatted)
        except:
            bill_per_person_formatted = f"N/A"
            return render_template(template_name_or_list="tip-calculator.html", FINAL_BILL_PER_PERSON=bill_per_person_formatted)
    return render_template(template_name_or_list="tip-calculator.html")


# BMI Calculator
@app.route(rule="/projects/bmi-calculator", methods=["GET", "POST"])
def bmi_calculator():
    """
    Calculates the Body Mass Index (BMI) based on user input.
    - On POST request: calculates the BMI, determines the BMI range, and provides relevant information.
    - On GET request: renders the BMI calculator form.
    """
    bmi_ranges = {
        "Underweight": "Your BMI indicates that you are underweight for your height. It's important to ensure you're getting enough nutrition to support your health and well-being. Consider consulting with a healthcare professional to determine a healthy approach to gaining weight.", 
        "Normal weight": "Congratulations! Your BMI falls within the normal weight range for your height. This indicates a healthy weight, which is associated with a lower risk of developing weight-related health problems. Keep up the good work with your healthy lifestyle!", 
        "Overweight": "Your BMI suggests that you are overweight for your height. This can increase your risk of developing health problems like heart disease, high blood pressure, and type 2 diabetes. Consider making lifestyle changes such as eating a balanced diet and increasing physical activity to achieve a healthier weight.", 
        "Obese": "Your BMI indicates that you are in the obese range for your height. Obesity significantly increases your risk of developing serious health conditions, including heart disease, stroke, type 2 diabetes, and certain cancers. It's important to prioritize healthy eating habits, regular physical activity, and possibly seek guidance from a healthcare provider to manage your weight and improve your overall health."
    }
    if request.method == "POST":
        try:
            data = request.form
            height_ft = int(data["heightFeet"])
            height_in = float(data["heightInches"])
            total_height_in = (height_ft * 12) + height_in
            weight = float(data["weight"])
            bmi = (weight * 703) / (total_height_in ** 2)
            bmi_rounded = round(bmi, 2)
            if bmi_rounded < 18.5:
                bmi_range = "Underweight"
            elif bmi_rounded < 25:
                bmi_range = "Normal weight"
            elif bmi_rounded < 30:
                bmi_range = "Overweight"
            else:
                bmi_range = "Obese"
            bmi_formatted = f"{bmi_rounded:.2f}"
            return render_template(template_name_or_list="bmi-calculator.html", BMI_FORMATTED=bmi_formatted, BMI_RANGE=bmi_range, BMI_RANGE_INFO=bmi_ranges[bmi_range])
        except:
            bmi_formatted = f"N/A"
            return render_template(template_name_or_list="bmi-calculator.html", BMI_FORMATTED=bmi_formatted)
    return render_template(template_name_or_list="bmi-calculator.html")


# Life in Weeks
@app.route(rule="/projects/life-in-weeks", methods=["GET", "POST"])
def life_in_weeks():
    """
    Calculates remaining weeks in a person's life based on current age.
    - On POST request: calculates and displays remaining weeks.
    - On GET request: renders the life in weeks calculator form.
    """
    if request.method == "POST":
        try:
            data = request.form
            current_age_years = float(data["ageYears"])
            years_remaining = 90 - current_age_years
            weeks_remaining = years_remaining * 52
            weeks_remaining_rounded = round(weeks_remaining)
            return render_template(template_name_or_list="life-in-weeks.html", WEEKS_REMAINING_ROUNDED=weeks_remaining_rounded)
        except:
            weeks_remaining_rounded = f"N/A"
            return render_template(template_name_or_list="life-in-weeks.html", WEEKS_REMAINING_ROUNDED=weeks_remaining_rounded)
    return render_template(template_name_or_list="life-in-weeks.html")


# Leap Year Checker
@app.route(rule="/projects/leap-year-checker", methods=["GET", "POST"])
def leap_year_checker():
    """
    Checks if a given year is a leap year.
    - On POST request: checks and displays leap year result.
    - On GET request: renders the leap year checker form.
    """
    if request.method == "POST":
        try:
            data = request.form
            year = int(data["year"])
            if year % 4 == 0:
                if year % 100 == 0:
                    if year % 400 == 0:
                        leap_year_result = f"{year} is a Leap Year"
                    else:
                        leap_year_result = f"{year} is not a Leap Year"
                else:
                    leap_year_result = f"{year} is a Leap Year"
            else:
                leap_year_result = f"{year} is not a Leap Year"
            return render_template(template_name_or_list="leap-year-checker.html", LEAP_YEAR_RESULT=leap_year_result)
        except:
            leap_year_result = f"N/A"
            return render_template(template_name_or_list="leap-year-checker.html", LEAP_YEAR_RESULT=leap_year_result)
    return render_template(template_name_or_list="leap-year-checker.html")


# Heads or Tails
@app.route(rule="/projects/heads-or-tails", methods=["GET", "POST"])
def heads_or_tails():
    """
    Simulates a coin flip (heads or tails).
    - On POST request: randomly generates and displays a coin flip result.
    - On GET request: renders the heads or tails game interface.
    """
    coin = {
        0: "Heads", 
        1: "Tails"
    }
    if request.method == "POST":
        coin_flip = coin[random.randint(0, 1)]
        return render_template(template_name_or_list="heads-or-tails.html", COIN_FLIP=coin_flip)
    return render_template(template_name_or_list="heads-or-tails.html")


# Rocks, Paper, Scissors
@app.route(rule="/projects/rock-paper-scissors", methods=["GET", "POST"])
def rock_paper_scissors():
    """
    Simulates a rock-paper-scissors game against the computer.
    - On POST request: evaluates player's choice against computer's random choice and determines the winner.
    - On GET request: renders the rock-paper-scissors game interface.
    """
    hand = {
        0: "Rock", 
        1: "Paper", 
        2: "Scissors"
    }
    if request.method == "POST":
        data = request.form
        player_hand = data["choice"]
        ai_hand = hand[random.randint(0, 2)]
        if player_hand == ai_hand:
            result = "It's a tie!"
        elif (player_hand == "Rock" and ai_hand == "Scissors") or \
             (player_hand == "Paper" and ai_hand == "Rock") or \
             (player_hand == "Scissors" and ai_hand == "Paper"):
            result = "You win!"
        else:
            result = "You lose!"
        return render_template(template_name_or_list="rock-paper-scissors.html", PLAYER_HAND=player_hand, AI_HAND=ai_hand, RESULT=result)
    return render_template(template_name_or_list="rock-paper-scissors.html")


# Gender Guesser
@app.route(rule="/projects/gender-guesser", methods=["GET", "POST"])
def gender_guesser():
    """
    Predicts the gender based on a given name using an external API.
    - On POST request: fetches and displays the predicted gender and probability.
    - On GET request: renders the gender guesser form.
    """
    if request.method == "POST":
        data = request.form
        name = data["name"]
        api_params = {
            "name": name
        }
        genderize_response = requests.get(GENDERIZE_API_ENDPOINT, params=api_params)
        genderize_response.raise_for_status()
        genderize_data = genderize_response.json()
        gender_data = genderize_data["gender"]
        gender_probability = genderize_data["probability"]
        try:
            result = f"{gender_data.title()} (Probability: {float(gender_probability) * 100}%)"
        except AttributeError:
            result = "N/A"
        return render_template(template_name_or_list="gender-guesser.html", GENDER_DATA=result)
    return render_template(template_name_or_list="gender-guesser.html")


# Age Guesser
@app.route(rule="/projects/age-guesser", methods=["GET", "POST"])
def age_guesser():
    """
    Predicts the age based on a given name using an external API.
    - On POST request: fetches and displays the predicted age.
    - On GET request: renders the age guesser form.
    """
    if request.method == "POST":
        data = request.form
        name = data["name"]
        api_params = {
            "name": name
        }
        ageify_response = requests.get(AGEIFY_API_ENDPOINT, params=api_params)
        ageify_response.raise_for_status()
        ageify_data = ageify_response.json()
        age_data = ageify_data["age"]
        if age_data == None:
            age_data = "N/A"
        return render_template(template_name_or_list="age-guesser.html", AGE_DATA=age_data)
    return render_template(template_name_or_list="age-guesser.html")


# City Coordinates Finder
@app.route(rule="/projects/city-coordinates-finder", methods=["GET", "POST"])
def city_coordinates_finder():
    """
    Finds and displays the coordinates (latitude and longitude) of a given city.
    - On POST request: fetches and displays the coordinates for the specified city.
    - On GET request: renders the city coordinates finder form.
    """
    if request.method == "POST":
        try:
            data = request.form
            city = data["city"]
            state_country = data["state-country"]
            api_params = {
                "q": f"{city}, {state_country}", 
                "appid": OPENWEATHERMAP_API_KEY
            }
            geocoding_response = requests.get(GEOCODING_API_ENDPOINT, params=api_params)
            geocoding_response.raise_for_status()
            geocoding_data = geocoding_response.json()
            result_data = geocoding_data[0]
            result_city = result_data["name"]
            result_country = result_data["country"]
            result_state = result_data["state"]
            result_latitude = result_data["lat"]
            result_longitude = result_data["lon"]
            result_location = f"Location: {result_city}, State: {result_state}, Country: {result_country}"
            result = f"Latitude: {result_latitude}, Longitude: {result_longitude}"
            return render_template(template_name_or_list="city_coordinates_finder.html", RESULT_LOCATION=result_location, RESULT=result)
        except KeyError:
            return render_template(template_name_or_list="city_coordinates_finder.html")
        except IndexError:
            return render_template(template_name_or_list="city_coordinates_finder.html")
    return render_template(template_name_or_list="city_coordinates_finder.html")


# 24 Hour Weather Forecaster
@app.route(rule="/projects/weather-forecaster", methods=["GET", "POST"])
def weather_forecaster():
    """
    Fetches and displays the 24-hour weather forecast for a specified city.
    - On POST request: fetches and displays weather forecast data for the specified city.
    - On GET request: renders the weather forecaster form.
    """
    forecast = False
    if request.method == "POST":
        forecast = True
        # Generate forecast hours dynamically
        hour1 = f"{(datetime.datetime.now() + datetime.timedelta(hours=3)).hour % 12}:00"
        hour2 = f"{(datetime.datetime.now() + datetime.timedelta(hours=6)).hour % 12}:00"
        hour3 = f"{(datetime.datetime.now() + datetime.timedelta(hours=9)).hour % 12}:00"
        hour4 = f"{(datetime.datetime.now() + datetime.timedelta(hours=12)).hour % 12}:00"
        hour5 = f"{(datetime.datetime.now() + datetime.timedelta(hours=15)).hour % 12}:00"
        hour6 = f"{(datetime.datetime.now() + datetime.timedelta(hours=18)).hour % 12}:00"
        hour7 = f"{(datetime.datetime.now() + datetime.timedelta(hours=21)).hour % 12}:00"
        hour8 = f"{(datetime.datetime.now() + datetime.timedelta(hours=24)).hour % 12}:00"
        hours = [hour1, hour2, hour3, hour4, hour5, hour6, hour7, hour8]
        
        data = request.form
        city = data["city"]
        state_country = data["state-country"]
        
        # Fetch city coordinates
        geocoding_api_params = {
            "q": f"{city}, {state_country}", 
            "appid": OPENWEATHERMAP_API_KEY
        }
        geocoding_response = requests.get(GEOCODING_API_ENDPOINT, params=geocoding_api_params)
        geocoding_response.raise_for_status()
        geocoding_data = geocoding_response.json()
        result_data = geocoding_data[0]
        result_city = result_data["name"]
        result_country = result_data["country"]
        result_state = result_data["state"]
        result_latitude = float(result_data["lat"])
        result_longitude = float(result_data["lon"])
        result_location = f"Location: {result_city}, State: {result_state}, Country: {result_country}"
        
        # Fetch weather forecast
        openweathermap_api_params = {
            "lat": result_latitude, 
            "lon": result_longitude, 
            "appid": OPENWEATHERMAP_API_KEY, 
            "units": "imperial", 
            "cnt": 8
        }
        openweathermap_response = requests.get(OPENWEATHERMAP_API_ENDPOINT, params=openweathermap_api_params)
        openweathermap_response.raise_for_status()
        openweathermap_data = openweathermap_response.json()
        results = openweathermap_data["list"]
        
        return render_template(template_name_or_list="weather-forecaster.html", FORECAST=forecast, RESULT_LOCATION=result_location, HOURS=hours, RESULTS=results)
    
    return render_template(template_name_or_list="weather-forecaster.html", FORECAST=forecast)


# Workout Calculator
@app.route(rule="/projects/workout-calculator", methods=["GET", "POST"])
def workout_calculator():
    calculate_workout = None
    if request.method == "POST":
        try:
            data = request.form
            weight_lb = float(data["weight"])
            weight_kg = int(weight_lb / 2.2046)
            height_ft = int(data["heightFeet"])
            height_in = float(data["heightInches"])
            total_height_in = float((height_ft * 12) + height_in)
            height_cm = int(total_height_in * 2.54)
            age = int(data["age"])
            query = data["query"]
            nutritionix_params = {
                "query": query,
                "weight_kg": weight_kg,
                "height_cm": height_cm,
                "age": age
            }
            nutritionix_response = requests.post(url=NUTRITIONIX_ENDPOINT, headers=NUTRITIONIX_HEADERS, json=nutritionix_params)
            nutritionix_result = nutritionix_response.json()
            result = nutritionix_result["exercises"][0]
            calculate_workout = True
            return render_template(template_name_or_list="workout-calculator.html", CALCULATE_WORKOUT=calculate_workout, RESULT=result)
        except ValueError:
            calculate_workout = False
            return render_template(template_name_or_list="workout-calculator.html", CALCULATE_WORKOUT=calculate_workout)
    return render_template(template_name_or_list="workout-calculator.html", CALCULATE_WORKOUT=calculate_workout)


if __name__ == "__main__":
    app.run(debug=False)
