from flask import Flask, render_template, url_for
app = Flask(__name__)


dummy_data = [

    {
        'rank' : 1,
        'player' : 'suri',
        'points' : 999
    },
    {
        'rank' : 2,
        'player' : 'Zawsze Razem',
        'points' : 997
    },
    {
        'rank' : 3,
        'player' : 'Aracurya',
        'points' : 777
    },
    {
        'rank' : 4,
        'player' : 'MUM',
        'points' : 69
    },
    {
        'rank' : 5,
        'player' : 'H',
        'points' : 4
    },

]


# The main landing page
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

# Page displaying the ranking
@app.route('/manhunt')
def manhunt():
    return render_template('ranking.html', data=dummy_data, title = 'Manhunt | Assassins\' Network', mode='Manhunt' )

@app.route('/escort')
def escort():
    return render_template('ranking.html', data=dummy_data, title = 'Escort | Assassins\' Network', mode='Escort' )

# Page showing the algorithm used
@app.route('/elo')
def elo():
    return render_template('elo.html', title = 'Elo Explained | Assassins\' Network' )

# Page with additional informaction
@app.route('/about')
def about():
    return render_template('about.html', title = 'About Assassins\' Network')

if __name__ == '__main__':
    app.run(debug=True)
