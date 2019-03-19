import requests
import json

url = 'http://www.omdbapi.com/?apikey=8777274b&i='
class fetchOmdb:
    
    def __init__(self):
        pass

    # fetching data from omdb api
    def fetcher(self,imdb_id):
        
        jsonArr = []

        for imdbId in imdb_id:
            furl = url + imdbId
            print(furl)
            r = requests.get(furl)
            json_object = r.text
            jsonArr.append(json.loads(json_object))
            break
        return jsonArr

    # converting dat in json format to array of dictionary
    def present(self,imdb_id):
        
        jsonArr = self.fetcher(imdb_id)
        finalArr = []

        for json in jsonArr:
            Dict = {}
            Dict['imdbID'] = json['imdbID']
            Dict['Title'] = json['Title']
            Dict['Released'] = json['Released']
            Dict['Year'] = json['Year']
            Dict['Director'] = json['Director']
            Dict['Genre'] = json['Genre']
            Dict['Writer'] = json['Writer']
            Dict['Actors'] = json['Actors']
            Dict['Plot'] = json['Plot']
            Dict['Poster'] = json['Poster']
            Dict['imdbRating'] = json['imdbRating']
            Dict['Runtime'] = json['Runtime']
            finalArr.append(Dict)

        return finalArr


