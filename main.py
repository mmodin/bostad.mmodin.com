from flask import Flask, render_template, request
from html_table import html_table
from bf import BF
from yaml import load
from time import time
from werkzeug.contrib.cache import SimpleCache


app = Flask(__name__)
cache = SimpleCache()
with open('config.yml', 'r') as f:
    config = load(f)
 

def get_bf():
    bf = cache.get('bf')
    if bf is None:
        bf = BF(
            login=True,
            detail=True,
            username=config['username'],
            password=config['password']
        )
        cache.set('bf', bf, timeout=5 * 60)
    return bf


@app.route('/')
def index():
    print("Got request from ip: {}".format(request.remote_addr))
    start = time()
    print("Starting data download")
    bf = get_bf()
    table = html_table(bf.get_relevant_data())
    seconds = round(time() - start, 3)
    return render_template('table.html', table=table, time=seconds, latest=bf.latest)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='8080', debug='True')
