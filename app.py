from flask import Flask, render_template, request, jsonify,redirect, url_for
from newsapi import NewsApiClient
import requests
from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb+srv://admin-Margesh:margesh@cluster0.dgnbguu.mongodb.net/my_database')

db = client.my_database

collection = db.stock_purchases

app = Flask(__name__,template_folder='template')
newsapi = NewsApiClient(api_key='cee991a398714f73b50fd6acf20f1a94')
recommended_stocks = [
    'PAYTM', 'INFY', 'RELIANCE', 'WIPRO', 'TCS'
]

def get_pe_ratios():
    pe_ratios = {}
    api_key = '8KO6U7YFARRYWCP7'

    for stock_symbol in recommended_stocks:
        url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={stock_symbol}&apikey={api_key}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'PERatio' in data:
                pe_ratio = float(data['PERatio'])
                pe_ratios[stock_symbol] = pe_ratio
    
    return pe_ratios

def get_top_pe_stocks(pe_ratios):
    
    top_3_stocks = sorted(pe_ratios.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return top_3_stocks

def get_stock_data(stockname):
    api_key = "8KO6U7YFARRYWCP7"
    # 8KO6U7YFARRYWCP7
    # "B5XAXDDE2YCPBEVH"
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stockname}&outputsize=compact&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'Time Series (Daily)' in data:
            time_series_data = data['Time Series (Daily)']
            return time_series_data
        
    print(f"Error: {response.status_code}, {response.text}")
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/re.html')
def top_pe_stocks():
    pe_ratios = get_pe_ratios()
    top_stocks = get_top_pe_stocks(pe_ratios)
    return render_template('re.html', top_stocks=recommended_stocks)

@app.route("/buy.html")
def buy():
    return render_template('buy.html',recommended_stocks=recommended_stocks)


@app.route('/buy_stock', methods=['POST'])
def buy_stock():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        
        purchase_data = {
            'stock_symbol': stock_symbol,
            'purchase_date': datetime.now()
        }
        

        collection.insert_one(purchase_data)
        
        # Redirect back to the recommended stocks page
        return redirect('/')

@app.route("/search.html")
def search():
    return render_template('search.html')

@app.route('/portfolio.html')
def display_purchases():
    # Retrieve the data from the MongoDB collection
    purchases = list(collection.find())
    
    # Pass the data to the 'purchases.html' template
    return render_template('portfolio.html', purchases=purchases)

@app.route('/news.html')
def news():
    all_articles = newsapi.get_everything(
        q='stock market', 
        language='en'
    )

    return render_template('news.html', top_headlines=all_articles)

@app.route('/get_data', methods=['POST'])
def get_data():
    stockname = request.form['stockname']
    time_series_data = get_stock_data(stockname)
    if time_series_data:
        return render_template('chart.html', stockname=stockname, time_series_data=time_series_data)
    else:
        return jsonify({"error": "No data found for the given stock."})
        

if __name__ == '__main__':
    app.run(debug=True)

