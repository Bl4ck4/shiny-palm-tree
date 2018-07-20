from flask import Flask, render_template
from datetime import datetime
import calendar

now = datetime.now()
months = [" ","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Nov","Dec"]

app = Flask(__name__)

@app.route("/")
def main():
    thisMonth = months[now.month]
    days = calendar.monthrange(now.year,now.month)
    return render_template('index.html',i=1,year=now.year,month=thisMonth,days=days)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
