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
            json_object = r.json
            jsonArr.append(json.loads(r.text))
            break

        return jsonArr
    # converting dat in json format to array of dictionary
    def present(self,imdb_id):
        
        jsonArr = self.fetcher(imdb_id)
        finalArr = []

        for json in jsonArr:
            Dict = {}
            print(json['Title'])
            #Dict['Released'] = json['Released']
            #Dict['Year'] = json['Year']
            #Dict['Director'] = json['Director']
            #Dict['Genre'] = json['Genre']
            #Dict['Writer'] = json('Writer')

            finalArr.append(Dict)

        return finalArr



obj = fetchOmdb()
print(obj.present(imdb_id = ['tt0081505', 'tt0054215', 'tt0078748', 'tt4972582', 'tt1156398', 'tt0090605', 'tt1457767', 'tt5052448', 'tt0073195', 'tt0365748', 'tt0387564', 'tt0070047', 'tt3065204', 'tt0289043', 'tt0408236']
))