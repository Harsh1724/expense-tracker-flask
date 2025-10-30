from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
FILE_NAME = "expenses.csv"

# Ensure CSV exists
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
    df.to_csv(FILE_NAME, index=False)

def load_data():
    return pd.read_csv(FILE_NAME)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    category = request.form['category']
    amount = request.form['amount']
    desc = request.form['description']

    if not date or not amount:
        return "Missing required fields", 400

    df = load_data()
    new = pd.DataFrame([[date, category, float(amount), desc]], columns=df.columns)
    df = pd.concat([df, new], ignore_index=True)
    save_data(df)
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    df = load_data()
    if df.empty:
        return render_template('dashboard.html', chart_html=None, total=0, data=[])

    df['Amount'] = df['Amount'].astype(float)
    total = df['Amount'].sum()

    # Plotly interactive chart
    grouped = df.groupby('Category')['Amount'].sum().reset_index()
    fig = px.pie(grouped, names='Category', values='Amount', title='Expense by Category', color_discrete_sequence=px.colors.qualitative.Pastel)
    chart_html = pio.to_html(fig, full_html=False)

    data = df.to_dict(orient='records')
    return render_template('dashboard.html', chart_html=chart_html, total=total, data=data)

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
