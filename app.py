import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'k92OlA#c69Qv8m1!'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


#Api call for current weather   
def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=e21e920bd8118842c29934ddc6d4974f'
    r = requests.get(url).json()
    return r

#Api for weather forecaste
def get_forecast_data(city):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={ city }&units=metric&appid=e21e920bd8118842c29934ddc6d4974f'
    r = requests.get(url).json()
    return r

#Api call for historical weather
def get_history_data(city):
    #url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{ city }/last7days?unitGroup=metric&key=MQPK63GN7CXF4XH2DH6BRD9C4'
    url = f'https://api.weatherbit.io/v2.0/history/daily?city={ city }&start_date=2021-07-01&end_date=2021-07-07&key=7b9b5a6324124d17b5ed2891c83e0776'
    r = requests.get(url).json()
    return r



#current weather section (This is the home route too)
@app.route('/')
def index_get():
    cities = City.query.all()

    weather_data = []

    for city in cities:

        data = get_weather_data(city.name)
    

    weather = {
        'city' : city.name,
        'temperature' : data['main']['temp'],
        'humidity' : data['main']['humidity'],
        'pressure' : data['main']['pressure'],
        'wind_speed' : data['wind']['speed'],
        'description' : data['weather'][0]['description'],
        'icon' : data['weather'][0]['icon'],
    }

    weather_data.append(weather)

    
    return render_template('current_weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    
    new_city = request.form.get('city')

    new_city_data = get_weather_data(new_city)
    
    #checks if the city exists
    if new_city_data['cod'] == 200:    
        new_city_obj = City(name=new_city)

        db.session.add(new_city_obj)
        db.session.commit()
    else:
        flash('City does not exist in the world!')
        

    return redirect(url_for('index_get'))



#weather forecast section
@app.route('/forecast')
def index2_get():
    cities = City.query.all()

    forecast_data = []

    for city in cities:

        data = get_forecast_data(city.name)
        

    for key in range(0,40,8):
        forecast = {
            'city' : city.name,
            'date':  data['list'][key]['dt_txt'],
            'temp': data['list'][key]['main']['temp'],
            'humidity': data['list'][key]['main']['humidity'],
            'pressure' : data['list'][key]['main']['pressure'],
            'wind':  data['list'][key]['wind']['speed'],
            'condition': data['list'][key]['weather'][0]['description'],
            'icon' : data['list'][key]['weather'][0]['icon'],
        }
        forecast_data.append(forecast)
    

    return render_template('forecast_weather.html', forecast_data=forecast_data)

@app.route('/forecast', methods=['POST'])
def index2_post():
    
    new_city = request.form.get('city')

    new_city_data = get_forecast_data(new_city)
    
    #checks if the city exists
    if new_city_data['cod'] == '200':         
        new_city_obj = City(name=new_city)
        db.session.add(new_city_obj)
        db.session.commit()
    else:                                  
        flash('City does not exist in the world!')

    
    return redirect(url_for('index2_get'))



#historical weather section
@app.route('/history')
def index3_get():

    cities = City.query.all()

    history_data = []
    
    for city in cities:
        data = get_history_data(city.name)
        

    for key in range(0,6):
        history = {
            'city' : city.name,
            'date':  data['data'][key]['datetime'],
            'temp': data['data'][key]['temp'],
            'humidity' : data['data'][key]['rh'],
            'wind' : data['data'][key]['wind_spd'],
        }
        history_data.append(history)

    return render_template('historical_weather.html', history_data=history_data)


@app.route('/history', methods=['POST'])
def index3_post():
    new_city = request.form.get('city')

    new_city_data = get_history_data(new_city)
    
    #checks if the city exists
    if new_city_data['city_name'] == new_city:
        new_city_obj = City(name=new_city)

        db.session.add(new_city_obj)
        db.session.commit()
    else:
        flash('City does not exist in the world!')

    return redirect(url_for('index3_get'))
