from flask import Flask, render_template

app = Flask('flaskwp1')
# webcode = open('webcode.html').read() - not needed

@app.route('/')
def webprint():
    return render_template('indexTweek2.html') 

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000)