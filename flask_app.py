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

def concat_results(*results):
   ids = set()
   for result in results:
       for v in result:
           if v['_id'] not in ids:
               ids.add(v['_id'])
               yield v

def extract_mode_data(mode):
    data = mongo.db.players.find({ f"{mode}games.total": { '$gte': 10 } }).sort(f"{mode}mmr",-1)
    tbd = mongo.db.players.find({'$and': [ {f"{mode}games.total": {"$gt": 0}}, {f"{mode}games.total": {"$lt": 10}}]}).sort(f"{mode}mmr", -1)
    return list(concat_results(data, tbd))

# Page displaying the ranking
@app.route('/manhunt')
def manhunt():
    data = extract_mode_data("mh")
    return render_template('ranking.html', data=data, title = 'Manhunt | Assassins\' Network', mode='Manhunt' )

@app.route('/escort')
def escort():
    data = extract_mode_data("e")
    return render_template('ranking.html', data=data, title = 'Escort | Assassins\' Network', mode='Escort' )

@app.route('/running')
def running():
    data = extract_mode_data("aar")
    return render_template('ranking.html', data=data, title = 'Artifact Assault Running | Assassins\' Network', mode='AA Running' )

@app.route('/defending')
def defending():
    data = extract_mode_data("aad")
    return render_template('ranking.html', data=data, title = 'Artifact Assault Defending | Assassins\' Network', mode='AA Defending' )

@app.route('/domination')
def domination():
    data = extract_mode_data("do")
    return render_template('ranking.html', data=data, title = 'Domination | Assassins\' Network', mode='Domination' )

@app.route('/allmodes')
def allmodes():
    modes = ["mh", "e", "aar", "aad", "do"]
    players = mongo.db.players.find({"$or": [{f"{m}games.total": {"$gte": 10}} for m in modes]})
    players = list(players)
    for p in players:
        p["totalmmr"] = 0
        p["totalgames"] = 0
        p["totalwins"] = 0
        p["totallosses"] = 0
        for m in modes:
            games = p[m + "games"]["total"]
            if games > 9:
                p["totalmmr"] += p[m + "mmr"]
            p["totalgames"] += games
            p["totalwins"] += p[m + "games"]["won"]
            p["totallosses"] += p[m + "games"]["lost"]
            p["totalmmr"] 
    players.sort(key=lambda p: p["totalmmr"], reverse=True)
    #players = players[:10]
    for i in range(len(players)):
        players[i]["totalrank"] = i + 1
    return render_template('ranking.html', data=players, title='All Modes | Assassins\' Network', mode='All Modes')

@app.route('/average')
def average():
    modes = ["mh", "e", "aar", "aad", "do"]
    players = mongo.db.players.find({"$or": [{f"{m}games.total": {"$gte": 10}} for m in modes]})
    players = list(players)
    for p in players:
        played_modes = 0
        p["totalmmr"] = 0
        p["totalgames"] = 0
        p["totalwins"] = 0
        p["totallosses"] = 0
        for m in modes:
            games = p[m + "games"]["total"]
            if games > 9:
                played_modes += 1
                p["totalmmr"] += p[m + "mmr"]
            p["totalgames"] += games
            p["totalwins"] += p[m + "games"]["won"]
            p["totallosses"] += p[m + "games"]["lost"]
            p["totalmmr"] 
        p["totalmmr"] /= played_modes
    players.sort(key=lambda p: p["totalmmr"], reverse=True)
    #players = players[:10]
    for i in range(len(players)):
        players[i]["totalrank"] = i + 1
    return render_template('ranking.html', data=players, title='Average | Assassins\' Network', mode='Average')

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

@app.route('/maps')
def maps():
    long_names = {
            "e": "Escort",
            "mh": "Manhunt",
            "do": "Domination",
            "aa": "Artifact Assault",
            }
    data = {}
    for mode in ["aa", "e", "mh", "do"]:
        modedata = mongo.db.maps.find({f"{mode}.games": {"$gt": 0}})
        modedata = [dict({"name": d["name"]}, **d[mode]) for d in modedata]
        modedata = list(modedata)
        if not len(modedata):
            data[long_names[mode]] = []
            continue
        average_rating = sum([m["hostrating"] for m in modedata]) / len(modedata)
        # switch out the rating for the displayed rating - probably dumb to do here tbh
        for i in range(len(modedata)):
            modedata[i]["hostrating"] = int(round((modedata[i]["hostrating"] / average_rating - 1) * 100))
        data[long_names[mode]] = modedata
    return render_template('maps.html', modes=long_names.values(), data=data, title='Map Statistics | Assassins\' Network')

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
    if len(badges) == 0:
        return ""
    # I already wrote the conversion like this it's quite inefficient but it's already done
    badge = transform_badges(badges)
    badges = badge.split("><")

    full = ""
    for b in badges:
        name = b[b.find("\"") + 1:b.find(">") - 1]
        full += f"{b}> {name}<br><"

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
    elif rank == "All-Star":
        medal = "&#11088"
    elif rank == "Custom":
        medal = badge["medal"]["HTML"]
    else:
        raise ValueError("Unknown rank! Options are: 1st, 2nd, 3rd, Trophy, Rookie, Special, All-Star, and Custom.")
    if rank in ["Trophy", "Special", "All-Star", "Custom"]:
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

    filtered = []
    irrelevant = []

    for b in badges:
        # some badges won't have modes - eg rookie of the season
        if b["mode"] != "all":
            # because AA obviously cares about both - no priority here for now
            if mode in ["AA Running", "AA Defending"]:
                if b["mode"] in ["AA Running", "AA Defending"]:
                    # appending would break the ordering
                    filtered.append(b)
                else:
                    irrelevant = [b] + irrelevant
            elif b["mode"] == mode:
                filtered.append(b)
                #filtered = [b] + filtered
            else:
                irrelevant = [b] + irrelevant
        else:
            filtered.append(b)
            #filtered = [b] + filtered
    i = 0
    while len(filtered) < limit:
        try:
            filtered = [irrelevant[i]] + filtered
            i += 1
        except:
            break
    return filtered

# WE CAN'T RUN A LIVE APP IN DEBUG MODE! 
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
