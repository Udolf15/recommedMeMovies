import pandas as pd
import numpy as np

imdbToId = pd.read_csv('data/movieImdbId.csv')


class converter:

    def __init__():
        pass
    

    def convert(imdbIds):
        
        return list(imdbToId.loc[imdbToId['imdbId'] == imdbIds]['movieId'])[0]

    def convertToimdbId(movieId):

        return imdbToId.loc[imdbToId['movieId'].isin(movieId)]