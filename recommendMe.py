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

import warnings; warnings.simplefilter('ignore')

gen_md = pd.read_csv('gen_md.csv')

class recommendMe():

    def __init__(self):
        pass
    
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
