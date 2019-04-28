import pandas as pd
import numpy as np
from scipy import stats
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
from surprise import Reader, Dataset, SVD, evaluate
from imdbToId import converter

# Configuring database
import MySQLdb

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="udolf",         # your username
                     password="root",  # your password
                     db="recommendme")        # name of the data base


gen_md = pd.read_csv('data/gen_md.csv')

# Main recommendation part for the 

class recommendMe():

    def __init__(self):
        pass
    
    '''
    This will return movies intially to the guest who is not logged in or haven't rated a single
    movie
    '''

    def build_chart(genre, percentile=0.85):
        movieDb = gen_md[gen_md['genre'] == genre]
        vote_counts = movieDb[movieDb['vote_count'].notnull()]['vote_count'].astype('int')
        vote_averages = movieDb[movieDb['vote_average'].notnull()]['vote_average'].astype('int')
        C = vote_averages.mean()
        m = vote_counts.quantile(percentile)

        qualified = movieDb[(movieDb['vote_count'] >= m) & (movieDb['vote_count'].notnull()) & (movieDb['vote_average'].notnull())][['title','vote_count','vote_average','popularity','imdb_id']]
        qualified['vote_count'] = qualified['vote_count'].astype('int')
        qualified['vote_average'] = qualified['vote_average'].astype('int')
    
        qualified['wr'] = qualified.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) + (m/(m+x['vote_count']) * C), axis=1)
        qualified = qualified.sort_values('wr', ascending=False).head(250)
        return qualified.head(7)

    '''
    This will return movies that are top of their genre but not rated by the user
    '''

    def build_chartP(genre,userId, percentile=0.85):

        cur = db.cursor()

        result = cur.execute('SELECT * FROM ratings WHERE userId = %s',[userId])
        imdbIdsRatedAlready = []
        if(result > 0):
            data = cur.fetchall()
            for singleR in data:
                imdbIdsRatedAlready.append(singleR[3])

        cur.close()
        print(imdbIdsRatedAlready)
        movieDb = gen_md[gen_md['genre'] == genre]
        vote_counts = movieDb[movieDb['vote_count'].notnull()]['vote_count'].astype('int')
        vote_averages = movieDb[movieDb['vote_average'].notnull()]['vote_average'].astype('int')
        C = vote_averages.mean()
        m = vote_counts.quantile(percentile)

        qualified = movieDb[(movieDb['vote_count'] >= m) & (movieDb['vote_count'].notnull()) & (movieDb['vote_average'].notnull())][['title','vote_count','vote_average','popularity','imdb_id']]
        qualified['vote_count'] = qualified['vote_count'].astype('int')
        qualified['vote_average'] = qualified['vote_average'].astype('int')
    
        qualified['wr'] = qualified.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) + (m/(m+x['vote_count']) * C), axis=1)
        qualified = qualified.sort_values('wr', ascending=False).head(250)
        
        qualified = qualified[~qualified.imdb_id.isin(imdbIdsRatedAlready)]

        return qualified.head(8)

    ''' This function will take user id,5 movie and 5 rating from the database  that are 
    recently added and add them to the rating dataset that will be used for training the model
    '''

    def svdRecommender(userList,movieIdList,ratingList):
        # Adding the data form the user
        mat = []
        for i in range(len(ratingList)):
            temp = []
            temp.append(userList[i])
            temp.append(movieIdList[i])
            temp.append(ratingList[i])
            mat.append(temp)


        ratings_small = pd.read_csv('data/ratings_small.csv')

        newData = pd.DataFrame(mat,columns = ['userId','movieId','rating'])

        ratings_small = ratings_small.append(newData,ignore_index = True)

        ratings_small.to_csv('ratings_small.csv',index = False)
        # Getting the recommended movies after the training
        movies = recommendMe.recommender(userList[0])

        return movies


    ''' This function will take the user id and perform the svd decompostion from the rating data
        and after training, the trained model will we used to recommend the rating for all the 
        movies for the user and we will remove the movies which are already rated by the user
    '''
    def recommender(user):
    
        cur = db.cursor()
        # Getting the movies already rated by the user
        result = cur.execute('SELECT * FROM ratings WHERE userId = %s',[user])
        imdbIdsRatedAlready = []
        if(result > 0):
            data = cur.fetchall()
            for singleR in data:
                imdbIdsRatedAlready.append(singleR[3])

        cur.close()
        print(imdbIdsRatedAlready)

        ratings = pd.read_csv('data/ratings_small.csv')
        dataFrame = ratings['movieId'].unique()
        movies = pd.DataFrame([dataFrame],['movieId']).transpose()
        # Performing the training by using surprise package
        reader = Reader()
        data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
        data.split(n_folds=2)
        svd = SVD()
        evaluate(svd, data, measures=['RMSE', 'MAE'])
        trainset = data.build_full_trainset()
        svd.train(trainset)
        # Performing the prediction for each movie according to the user    
        movies['est'] = movies['movieId'].apply(lambda x : svd.predict(int(user),x).est)
        movies = movies.sort_values('est', ascending=False)

        movies = converter.convertToimdbId(list(movies.head(100)['movieId']))
        # Removing movies already rated by user
        print(movies)
        movies = movies[~movies.imdbId.isin(imdbIdsRatedAlready)]
        movies['imdbId'].values
        return movies
