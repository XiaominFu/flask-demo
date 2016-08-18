from flask import Flask, render_template, request, redirect
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.charts import TimeSeries
from bokeh.embed import components
import requests
import simplejson as json
import pandas as pd
import numpy as np

app = Flask(__name__)

app.vars={}

My_API_Key = 'INSERT_YOUR_API_KEY'

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:  #request was a POST
        app.vars['stock'] = request.form.get('stock_label')
        app.vars['price'] = request.form.getlist('price_type')
        return redirect('/stock_graph')

@app.route('/stock_graph', methods=['GET'])
def graph():
    stock = app.vars['stock'].upper()
    price_list = app.vars['price']
    api_url = "https://www.quandl.com/api/v3/datasets/WIKI/%s.json?api_key=%s" % (stock, My_API_Key)

    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    r = session.get(api_url)
    json_data = r.json()

    df = pd.DataFrame(json_data['dataset']['data'], columns=json_data['dataset']['column_names'])
    df['Date'] = pd.to_datetime(df['Date'])

    # Example: http://bokeh.pydata.org/en/latest/docs/reference/charts.html#timeseries
    plot = TimeSeries(df, x='Date', y=price_list, color=price_list, legend=True, active_scroll='wheel_zoom',
                      title="Data from Quandl WIKI set", ylabel='Price', xlabel='Date')

    plot.title.align = 'center'
    plot.title.text_font_size = '16pt'
    plot.title.text_font_style = 'normal'    

    script, div = components(plot)
    return render_template('graph.html', script=script, div=div, stock=stock)

if __name__ == '__main__':
    app.run(debug=False)
    #app.run(debug=True)