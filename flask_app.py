from flask import Flask, render_template, url_for
from flask_pymongo import PyMongo
from werkzeug.middleware.proxy_fix import ProxyFix
import json
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/public"
mongo = PyMongo(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

# The main landing page
@app.route('/')
@app.route('/home')
def home():
    data = mongo.db.home.find()
    return render_template('home.html', data=data)

# Page displaying the ranking
@app.route('/manhunt')
def manhunt():
    data = mongo.db.players.find({ "mhgames.total": { '$gte': 10 } }).sort("mhmmr",-1)
    return render_template('ranking.html', data=data, title = 'Manhunt | Assassins\' Network', mode='Manhunt' )

@app.route('/escort')
def escort():
    data = mongo.db.players.find({ "egames.total": { '$gte': 10 } }).sort("emmr",-1)
    return render_template('ranking.html', data=data, title = 'Escort | Assassins\' Network', mode='Escort' )

# Page showing the algorithm used
@app.route('/elo')
def elo():
    return render_template('elo.html', title = 'Elo Explained | Assassins\' Network' )

# Page with additional informaction
@app.route('/about')
def about():
    return render_template('about.html', title = 'About Assassins\' Network')

@app.route('/matches')
def matches():
    data = mongo.db.matches.find().sort("_id", -1).limit(20)
    return render_template('matches.html',data=data, title = 'Match History | Assassins\' Network')

@app.route('/players')
def players():
    data = mongo.db.players.find().collation({'locale':'en'}).sort("name")
    return render_template('players.html',data=data, title = 'Players | Assassins\' Network')

@app.route('/profile/<name>')
def display_profile(name):
    data = mongo.db.players.find_one({"name": name})
    data_matches = mongo.db.matches.find({"$or":[{"team1":{"$elemMatch":{"player":name}}}, {"team2":{"$elemMatch":{"player":name}}}]}).sort("_id", -1).limit(10)
    return render_template('profile.html',data=data, data_matches=data_matches, title = 'Player\'s Profile | Assassins\' Network')


#Jinja2 filters
@app.template_filter('winrate')
def winrate(w,l):
    try:
        winrate = (w*100)/(w+l)
        return "{0:.2f}%".format(winrate)
    except:
        return "0.00%"
    
@app.template_filter('kdratio')
def kdratio(k,d):
    try:
        kdr = k/d
        return "{0:.2f}".format(kdr)
    except:
        return "0.00"
    
@app.template_filter('avgscore')
def avgscore(s,g):
    try:
        avgs = s/g
        return "{0:.2f}".format(avgs)
    except:
        return "0.00"

# WE CAN'T RUN A LIVE APP IN DEBUG MODE! 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
