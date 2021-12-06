from flask import Flask, render_template, url_for
from flask_pymongo import PyMongo
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
import json
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/public"
mongo = PyMongo(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.errorhandler(Exception)
def error_handler():
    return redirect("https://assassins.network", code=302)

# The main landing page
@app.route('/')
@app.route('/home')
def home():
    data = mongo.db.home.find().sort("_id",-1).limit(7)
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

@app.route('/running')
def running():
    data = mongo.db.players.find({ "aargames.total": { '$gte': 10 } }).sort("aarmmr",-1)
    return render_template('ranking.html', data=data, title = 'Artifact Assault Running | Assassins\' Network', mode='Artifact Assault Running' )

@app.route('/defending')
def defending():
    data = mongo.db.players.find({ "aadgames.total": { '$gte': 10 } }).sort("aadmmr",-1)
    return render_template('ranking.html', data=data, title = 'Artifact Assault Defending | Assassins\' Network', mode='Artifact Assault Defending' )

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
    # load and search for all igns plus name so we don't get empty match histories
    igns = data["ign"]
    if type(igns) == str:
        igns = [igns]
    igns += [name]
    search = [{"team1":{"$elemMatch":{"player":ign}}} for ign in igns]
    search += [{"team2":{"$elemMatch":{"player":ign}}} for ign in igns]
    data_matches = mongo.db.matches.find({"$or": search}).sort("_id", -1).limit(10)
    return render_template('profile.html',data=data, data_matches=data_matches, title = 'Player\'s Profile | Assassins\' Network')

@app.route('/418')
def teapot():
    return render_template('418.html')

# Special tournament page
#@app.route('/tournament')
#def tournament():
#    return render_template('tournament.html', title = 'Tournament | Assassins\' Network' )

###End of pages

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

@app.template_filter('avgkills')
def avgkills(k,g):
    try:
        avgs = k/g
        return "{0:.2f}".format(avgs)
    except:
        return "0.00"

   
@app.template_filter('avgdeaths')
def avgdeaths(d,g):
    try:
        avgs = d/g
        return "{0:.2f}".format(avgs)
    except:
        return "0.00"

# WE CAN'T RUN A LIVE APP IN DEBUG MODE! 
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
