from flask import Flask, render_template, url_for
from flask_pymongo import PyMongo
from werkzeug.middleware.proxy_fix import ProxyFix
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
    data = mongo.db.players.find().sort("mhmmr",-1)
    return render_template('ranking.html', data=data, title = 'Manhunt | Assassins\' Network', mode='Manhunt' )

@app.route('/escort')
def escort():
    data = mongo.db.players.find().sort("emmr",-1)
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
    data = mongo.db.matches.find().sort("_id", -1)
    return render_template('matches.html',data=data, title = 'Match History | Assassins\' Network')

@app.route('/profile/<name>')
def display_profile(name):
    data = mongo.db.players.find_one({"ign": name})
    return render_template('profile.html',data=data, title = 'Player\'s Profile | Assassins\' Network')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
