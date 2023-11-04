from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import joblib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from login_validation import validate_login  # Import the validate_login function
import os

import warnings
warnings.filterwarnings("ignore")


app_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_directory)

app = Flask(__name__)
app.secret_key = '172a8e36f1e80b5068ef3dec6c707759'
# Load the pre-trained model
model = joblib.load('arima_model.pkl')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate the login
        result = validate_login(username, password)
        if result :
            session['username'] = username
            return redirect(url_for('input_form'))
        else:
            return render_template('login_error.html')

    return render_template('login.html')

@app.route('/input')
def input_form():
    if 'username' in session:
        return render_template('input.html')

@app.route('/submit', methods=['POST'])
def predict():
    
    # Create a DataFrame from the results
    df = pd.read_csv('stock_data.csv')



    # # Get user input for date
    cut_off_date = pd.to_datetime(request.form['date'])

    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by = 'date', inplace = True)
    df = df[df['date'] < cut_off_date]
    ts = df.set_index('date')['close']

    # # Get user input for the number of forecast periods
    # n_periods = int(request.json['n_periods'])

    n_periods = 20
    # Make predictions for the specified number of periods
    forecast, conf_int = model.predict(n_periods=n_periods, return_conf_int=True)

    # Create a date range for the forecasted periods
    forecast_dates = [ts.index[-1] + timedelta(days=i) for i in range(1, n_periods + 1)]

    # Prepare the forecasted values and dates for response
    forecast_data = [{'date': date.strftime('%Y-%m-%d'), 'value': value} for date, value in zip(forecast_dates, forecast)]


    # Create a plot of the forecast
    plt.plot(ts.index, ts.values, label='Observed', color='blue')
    plt.plot(forecast_dates, forecast, label='Forecast', color='red')
    plt.fill_between(forecast_dates, conf_int[:, 0], conf_int[:, 1], color='pink', alpha=0.5)
    plt.legend()
    plt.title('ARIMA Forecast')
    plt.xlabel('Date')
    plt.ylabel('Value')


    # Save the plot as an image
    plot_image_path = 'static/forecast_plot.png'
    plt.savefig('static/forecast_plot.png')

    plt.close()

    return redirect(url_for('output', image_filename='forecast_plot.png'))


@app.route('/back')
def back():
    return redirect(url_for('index'))


@app.route('/output')
def output():
    image_filename = 'forecast_plot.png'
    return render_template('output.html',  image_filename=image_filename)


if __name__ == '__main__':
    app.run(debug=True)
