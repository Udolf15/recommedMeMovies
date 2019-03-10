from flask import Flask, render_template , request ,flash , redirect, url_for, session, logging
from flask_mysqldb import MySQL
from recommendMe import recommendMe
from fetcherOmdb import fetchOmdb
from passlib.hash import sha256_crypt
# fetching the data from omdbapi
fetch = fetchOmdb()
genreList = ['Romance','Horror','Animation','Action','Crime','Thriller']
genreR = []

try:
    genreR.append(fetch.present(list(recommendMe.build_chart('Romance')['imdb_id'])))
    genreR.append(fetch.present(list(recommendMe.build_chart('Horror')['imdb_id'])))
    genreR.append(fetch.present(list(recommendMe.build_chart('Animation')['imdb_id'])))
    genreR.append(fetch.present(list(recommendMe.build_chart('Action')['imdb_id'])))
    genreR.append(fetch.present(list(recommendMe.build_chart('Crime')['imdb_id'])))
    genreR.append(fetch.present(list(recommendMe.build_chart('Thriller')['imdb_id'])))
    print("hell")
except:
    print('Exception Occured')

app = Flask(__name__)

# configuring DB

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'recommendmemovies'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#inti mysql

mysql = MySQL(app)



# webcode = open('webcode.html').read() - not needed
@app.route('/')
def webprint():
    if(len(genreR) != 0):
        return render_template('index.html',genreR = genreR,movieGen = genreList)
    else:
        return render_template('index.html',genreR = genreR)

# login route 
@app.route('/login' , methods= ['GET','POST'])
def login():
    if(request.method== 'POST'):
        userDetail = request.form
        userName = userDetail['username']
        userPassword = userDetail['password']

        cur = mysql.connection.cursor()
        # selecting user

        result = cur.execute("SELECT * FROM users WHERE username = %s",[userName])
        if(result>0):
            # get hash
            data = cur.fetchone()
            password = data['password']
            userId = data['id']
            # compare password

            if(sha256_crypt.verify(userPassword,password)):
                session['logged_in'] = True
                session['username'] = userName
                print("Redirect")
                return redirect(url_for('dashboard'))
            else:
                app.logger.info("Wrong password")
                print("wrong")
        else:
            app.logger.info("no User exists")
            print("no user")
        cur.close()

    return render_template('login.html')


#dashboard
@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()
    userD = cur.execute("SELECT * FROM users WHERE username = %s",[session['username']])
    userId = cur.fetchone()['id']
    result = cur.execute("SELECT * FROM ratings WHERE userId = %s",[userId])
    print('above')
    if(result>0):
        print('in')
        data = cur.fetchall()
        for singleR in data:
            print(singleR['movieId'])
            print(singleR['userId'])
            print(singleR['rating'])
    cur.close()
    return render_template('loggedin.html',genreR = genreR,movieGen = genreList)



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.clear()
    redirect(url_for(""))


# signup route
@app.route('/signup', methods = ['GET','POST'])
def signup():
    if(request.method == 'POST'):
        print("hello")
        userDetail = request.form
        userName = userDetail['username']
        userPassword = sha256_crypt.encrypt(str(userDetail['password']))
        userEmail = userDetail['email']
        userFName = userDetail['userFName']

        #create cursor
        print("Hello")
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",(userFName,userEmail,userName,userPassword))

        # commit

        mysql.connection.commit()
        cur.close()
        print("bye")

        return redirect(url_for('login'))
    return render_template('signup.html')
        


# details route
@app.route('/details/<imdbId>',methods = ['GET','POST'])
def details(imdbId):
    print("1")
    movieDetails = fetch.present([imdbId])[0]
    movieTitle = movieDetails['Title']
    moviePoster = movieDetails['Poster']
    movieReleased = movieDetails['Released']
    movieYear = movieDetails['Year']
    movieWriter = movieDetails['Writer']
    moviePlot = movieDetails['Plot']
    movieGenre = movieDetails['Genre']
    movieDirector = movieDetails['Director']
    movieIMDBRating = movieDetails['imdbRating']
    movieProduction = movieDetails['Production']
    movieRuntime = movieDetails['Runtime']
    movieActors = movieDetails['Actors']
    if(request.method == 'GET'):

        return render_template('movieDetails.html', movieTitle = movieTitle,
                                movieActors = movieActors,
                                moviePlot = moviePlot,
                                movieDirector = movieDirector,
                                movieGenre = movieGenre,
                                movieIMDBRating = movieIMDBRating,
                                moviePoster = moviePoster,
                                movieProduction = movieProduction,
                                movieRuntime = movieRuntime,
                                movieWriter = movieWriter,
                                movieYear = movieYear,
                                movieReleased = movieReleased)

    else:
        # getting the rating number
        ratingDetail = request.form
        rating = ratingDetail['comment[rating]']
        movieId = imdbId
        print(rating)
        print("Bitch")
        userId = None
        # checking if user is logged in if not then send the user to login page
        if(session.get('logged_in') == True):
            cur = mysql.connection.cursor()
            # selecting user

            result = cur.execute("SELECT * FROM users WHERE username = %s",[session['username']])
            if(result>0):
                data = cur.fetchone()
                # getting the userid
                userId = str(data['id'])

            cur.close()
        else:
            return redirect(url_for('login'))

        cur = mysql.connection.cursor()
        print("Hell")
        cur.execute("INSERT INTO ratings(userid,movieId,rating) VALUES(%s,%s,%s)",(userId,movieId,rating))
        print("done")
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key='bitchlasanga'
    app.run(host = '0.0.0.0', port = 3000)