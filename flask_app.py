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
    return render_template('ranking.html', data=data, title = 'Artifact Assault Running | Assassins\' Network', mode='AA Running' )

@app.route('/defending')
def defending():
    data = mongo.db.players.find({ "aadgames.total": { '$gte': 10 } }).sort("aadmmr",-1)
    return render_template('ranking.html', data=data, title = 'Artifact Assault Defending | Assassins\' Network', mode='AA Defending' )

@app.route('/domination')
def domination():
    data = mongo.db.players.find({ "dogames.total": { '$gte': 10 } }).sort("dommr",-1)
    return render_template('ranking.html', data=data, title = 'Domination | Assassins\' Network', mode='Domination' )

@app.route('/virtualtraining')
def vtraining():
    data = mongo.db.vtraining.find({})
    return render_template('vranking.html', data=data)

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
    return render_template('matches.html',data=data, page_no=0, title = 'Match History | Assassins\' Network')

#paginated matches
@app.route('/matches/<page>')
def paged_matches(page):
    try:
        page = int(page)
    except:
        data = mongo.db.matches.find().sort("_id", -1).limit(20)
        return render_template('matches.html',data=data, page_no=0, title = 'Match History | Assassins\' Network')
    page=max(0,page)
    data = mongo.db.matches.find().sort("_id", -1).skip(page*20).limit(20)
    return render_template('matches.html',data=data, page_no=page, title = 'Match History | Assassins\' Network')

@app.route('/players')
def players():
    data = mongo.db.players.find().sort("name")
    return render_template('players.html',data=data, title = 'Players | Assassins\' Network')

@app.route('/profile/<name>')
def display_profile(name):
    data = mongo.db.players.find_one({"name": name})
    # load and search for all igns plus name so we don't get empty match histories
    igns = data["ign"]
    if type(igns) == str:
        igns = [igns]
    if name not in igns:
        igns += [name]
    search = [{"team1":{"$elemMatch":{"player":ign}}} for ign in igns]
    search += [{"team2":{"$elemMatch":{"player":ign}}} for ign in igns]
    data_matches = mongo.db.matches.find({"$or": search}).sort("_id", -1).limit(10)
    return render_template('profile.html',data=data, data_matches=data_matches, title = 'Player\'s Profile | Assassins\' Network')

@app.route('/status')
def status_page():
    from status import status
    data = status.main()
    return render_template('status.html', data=data, title='Status Page | Assassins\' Network')

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
    
@app.template_filter('rank_title')
def rank_title(elo):
    if elo < 801:
        return "Disciple"
    if elo < 1000:
        return "Cleric"
    if elo < 1200:
        return "Cleric Supreme"
    if elo < 1400:
        return "Grand Cleric"
    return "Supreme Overlord Cleric"
    
@app.template_filter('rank_pic_small')
def rank_pic_small(elo):
    if elo < 801:
        return "badge_1_small.png"
    if elo < 1000:
        return "badge_2_small.png"
    if elo < 1200:
        return "badge_3_small.png"
    if elo < 1400:
        return "badge_4_small.png"
    return "badge_5_small.png"

@app.template_filter('rank_pic_big')
def rank_pic_big(elo):
    if elo < 801:
        return "badge_1_big.png"
    if elo < 1000:
        return "badge_2_big.png"
    if elo < 1200:
        return "badge_3_big.png"
    if elo < 1400:
        return "badge_4_big.png"
    return "badge_5_big.png"

# from Scripts/util.py
@app.template_filter("name_in_db")
def name_in_db(name):
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017')
    db = client.public
    try:
        import re
        rename = re.compile(name, re.IGNORECASE)
        player = db.players.find_one({"name" : rename})
        if player is None:
            player = db.players.find_one({"ign": rename})
        if player is None:
            raise ValueError(f"identify_player: player {name} not found")

        return f"<a href=\"/profile/{player['name']}\">{player['name']}</a>"
    except ValueError:
        return name

@app.template_filter("full_badge_names")
def full_badge_names(badges):
    # I already wrote the conversion like this it's quite inefficient but it's already done
    badge = transform_badges(badges)
    try:
        badges = badge.split("><")
    except:
        return ""

    full = ""
    for b in badges:
        name = b[b.find("\"") + 1:b.find(">") - 1]
        full += f"{b}> {name}<br><"

    if full in ["", ">"]:
        return ""

    return full[:-1].replace(">>", ">")

@app.template_filter("transform_badges")
def transform_badges(badges, mode=None):
    # we need to support no mode for user profiles
    if mode:
        badges = filter_badges(badges, mode)
    
    badges_str = ""

    for i in range(len(badges)):
        badges_str = transform_badge_to_html(badges[i], badges_str)
    return badges_str

def transform_badge_to_html(badge: dict, badges=""):
    # Ik there's a more elegant way of doing this but I don't have the time rn
    try:
        rank = badge["rank"]
    except:
        pass
    try:
        mode = badge["mode"]
    except:
        pass
    try:
        season = badge["season"]
    except:
        pass
    try:
        name = badge["name"]
    except:
        pass
    if rank == "1st":
        medal = "&#129351"
    elif rank == "2nd":
        medal = "&#129352"
    elif rank == "3rd":
        medal = "&#129353"
    elif rank == "Trophy":
        medal = "&#127942"
    elif rank == "Rookie":
        medal = "&#128304"
    elif rank == "Special":
        medal = "&#127941"
    else:
        raise ValueError("Unknown rank! Options are: 1st, 2nd, 3rd, Trophy, and Trophy.")
    if rank in ["Trophy", "Special"]:
        badges = f"<span title=\"{name}\">{medal}</span>" + badges
    elif rank == "Rookie":
        badges = f"<span title=\"Season {season} Rookie of the Season\">{medal}</span>" + badges
    else:
        badges = f"<span title=\"Season {season} {mode} {rank} Place\">{medal}</span>" + badges
    return badges

@app.template_filter("filter_badges")
def filter_badges(badges, mode):
    # the maximum number of badges to be displayed on a page
    limit = 5
    if len(badges) < limit + 1:
        return badges

    filtered = []
    irrelevant = []

    for b in badges:
        # some badges won't have modes - eg rookie of the season
        try:
            # because AA obviously cares about both - no priority here for now
            if mode in ["AA Running", "AA Defending"]:
                if b["mode"] in ["AA Running", "AA Defending"]:
                    filtered.append(b)
                else:
                    irrelevant.append(b)
            elif b["mode"] == mode:
                filtered.append(b)
            else:
                irrelevant.append(b)
        except:
            filtered.append(b)
    # irrelevant badges should be the wrong way around at this point
    irrelevant = irrelevant[::-1]
    i = 0
    while len(filtered) < limit:
        try:
            filtered.append(irrelevant[i])
            i += 1
        except:
            break
    return filtered

# WE CAN'T RUN A LIVE APP IN DEBUG MODE! 
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
