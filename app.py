from flask import Flask, render_template
from html_table import html_table
from bf import BF
from yaml import load


app = Flask(__name__)


@app.route("/")
def index():
    data = BF(
        login=True,
        detail=True,
        username=config['username'],
        password=config['password']
    )
    table = html_table(data.get_relevant_data())
    html = "<h3>Apartments currently listed: </h3><br /> %s <br />" % table
    #return html
    return render_template("table.html", table=table)


if __name__ == "__main__":
    with open('config.yml', 'r') as f:
        config = load(f)
    app.run()
