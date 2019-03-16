from flask import Flask, render_template , request ,flash , redirect, url_for, session, logging
from flask_mysqldb import MySQL
from recommendMe import recommendMe
from fetcherOmdb import fetchOmdb
from imdbToId import converter
from passlib.hash import sha256_crypt

# fetching the data from omdbapi
fetch = fetchOmdb()
genreList = ['Romance','Horror','Animation','Action','Thriller']
genreR = []
genreP = []
try:
    genreR.append(fetch.present(list(recommendMe.build_chart('Romance')['imdb_id'])))
    genreR.append(fetch.present(list(recommendMe.build_chart('Horror')['imdb_id'])))
    genreR.append(fetch.present(list(recommendMe.build_chart('Animation')['imdb_id'])))
    genreR.append(fetch.present(list(recommendMe.build_chart('Action')['imdb_id'])))
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

#init mysql

mysql = MySQL(app)


# home route or index route
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
            # if user has enterd right password we will load data personalized for the user
            if(sha256_crypt.verify(userPassword,password)):
                session['logged_in'] = True
                session['username'] = userName
                print("Redirect")
                personalizedList = []
                del genreP[:]
                genreP.append(fetch.present(list(recommendMe.build_chartP('Romance',userId)['imdb_id'])))
                genreP.append(fetch.present(list(recommendMe.build_chartP('Horror',userId)['imdb_id'])))
                genreP.append(fetch.present(list(recommendMe.build_chartP('Animation',userId)['imdb_id'])))
                genreP.append(fetch.present(list(recommendMe.build_chartP('Action',userId)['imdb_id'])))
                genreP.append(fetch.present(list(recommendMe.build_chartP('Thriller',userId)['imdb_id'])))
                
                movieD = cur.execute("SELECT * FROM users WHERE id = %s",[userId])
                x = cur.fetchone()
                print("X",x)
                if( x != None):
                    for i in range(10):
                        si = str(i+1)
                        movieI = "movie"+si
                        print("m",movieI)
                        print("x",x[movieI])
                        personalizedList.append(x[movieI])

                genreList.append('Mixed')
                genreP.append(fetch.present(personalizedList))
                
                return redirect(url_for('dashboard'))
            else:
                app.logger.info("Wrong password")
                print("wrong")
        else:
            app.logger.info("no User exists")
            print("no user")
        cur.close()

    return render_template('login.html')


#dashboard route
@app.route('/dashboard')
def dashboard():

    personalizedList = []

    cur = mysql.connection.cursor()
    userD = cur.execute("SELECT * FROM users WHERE username = %s",[session['username']])
    userId = cur.fetchone()['id']
    print("userId",userId)


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
    
    return render_template('loggedin.html',genreR = genreP,movieGen = genreList)


# logout route
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
        cur.execute("INSERT INTO users(name,email,username,password,rated) VALUES(%s,%s,%s,%s,%s)",(userFName,userEmail,userName,userPassword,"0"))

        # commit

        mysql.connection.commit()
        cur.close()
        print("bye")

        return redirect(url_for('login'))
    return render_template('signup.html')
        


# details route
# this route give the details of the movie
@app.route('/details/<imdbId>',methods = ['GET','POST'])
def details(imdbId):
    print("1")
    # First we get the details from the api using the fetcherOmdb file's class fetch
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
    movieRuntime = movieDetails['Runtime']
    movieActors = movieDetails['Actors']
    # if the request is get the we will show the details 
    # if the request is post that means the user has tried to rate the movie
    if(request.method == 'GET'):

        return render_template('movieDetails.html', movieTitle = movieTitle,
                                movieActors = movieActors,
                                moviePlot = moviePlot,
                                movieDirector = movieDirector,
                                movieGenre = movieGenre,
                                movieIMDBRating = movieIMDBRating,
                                moviePoster = moviePoster,
                                movieRuntime = movieRuntime,
                                movieWriter = movieWriter,
                                movieYear = movieYear,
                                movieReleased = movieReleased)

    else:
        # getting the rating number
        ratingDetail = request.form
        rating = str(ratingDetail['comment[rating]'])
        movieId = str(converter.convert(imdbId))
        print(type(imdbId))
        print(type(imdbId[0]))
        print(movieId)
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
                userRating = int(data['rated'])
                userRating = userRating + 1

            cur.execute("UPDATE users SET rated = %s WHERE id = %s",(userRating,userId))
            mysql.connection.commit()
            cur.close()
            print(userRating%5 == 0)
            if(userRating%5 == 0):
                # for each user if we found out that the user has rated more than 5 movies or a 
                # multiple of 5 then we will train the ml model and recommend the user movies
                del genreP[-1]
                del genreList[-1]
                if(userRating%20 == 0 ):
                    # here we are checking if the user have rated 20 movies we will also change the 
                    # genre movies also
                    del genreP[:]
                    genreP.append(fetch.present(list(recommendMe.build_chartP('Romance',userId)['imdb_id'])))
                    genreP.append(fetch.present(list(recommendMe.build_chartP('Horror',userId)['imdb_id'])))
                    genreP.append(fetch.present(list(recommendMe.build_chartP('Animation',userId)['imdb_id'])))
                    genreP.append(fetch.present(list(recommendMe.build_chartP('Action',userId)['imdb_id'])))
                    genreP.append(fetch.present(list(recommendMe.build_chartP('Crime',userId)['imdb_id'])))
                    genreP.append(fetch.present(list(recommendMe.build_chartP('Thriller',userId)['imdb_id'])))

                cur = mysql.connection.cursor()
                movieIdList = []
                ratingList = []
                userList = []
                print(type(userId))
                result = cur.execute("SELECT * FROM ratings WHERE userId = %s",[userId])

                data = cur.fetchall()
                
                # selecting the latest 5 and adding them to the rating_small.csv
                counter = 0
                for singleEntry in reversed(data):
                    movieIdList.append(singleEntry['movieId'])
                    ratingList.append(singleEntry['rating'])
                    userList.append(userId)
                    counter= counter+1
                    if(counter == 5):
                        break


                # here we first add the ratings to the rating csv and update the ratings_small.csv with new data
                movies = recommendMe.svdRecommender(userList,movieIdList,ratingList).values
                moviesL = []

                for movie in movies:
                    moviesL.append(movie[1])
                cur = mysql.connection.cursor()
                
                cur.execute("UPDATE users SET movie1 = %s,movie2 = %s,movie3 = %s,movie4 = %s,movie5 = %s,movie6 = %s,movie7 = %s,movie8 = %s,movie9 = %s,movie10 = %s WHERE id = %s",
                (moviesL[0],moviesL[1],moviesL[2],moviesL[3],moviesL[4],moviesL[5],moviesL[6],moviesL[7],moviesL[8],moviesL[9],userId))
                

                personalizedList = []
                movieD = cur.execute("SELECT * FROM users WHERE id = %s",[userId])
                x = cur.fetchone()
                print("X",x)
                if( x != None):
                    for i in range(10):
                        si = str(i+1)
                        movieI = "movie"+si
                        print("m",movieI)
                        print("x",x[movieI])
                        personalizedList.append(x[movieI])


                genreP.append(fetch.present(personalizedList))
                genreList.append("Mixed")
                cur.close()

                cur.close()
                

        else:
            return redirect(url_for('login'))

        cur = mysql.connection.cursor()
        print("Hell")
        print(type(userId),type(movieId),type(rating),type(imdbId))
        cur.execute("INSERT INTO ratings(userid,movieId,imdbId,rating) VALUES(%s,%s,%s,%s)",(userId,movieId,imdbId,rating))
        print("done")
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key='bitchlasanga'
    app.run(host = '0.0.0.0', port = 3000)