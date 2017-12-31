import json


class Movie:

    def __init__(self, dic, transform=True):
        if transform:
            # all fields are declared here, although they may change value
            self.title = dic['Title']
            self.released = int(dic['Year'][4:])  # year # @ tochange
            self.rated = dic['Rated']
            self.genre = dic['Genre']
            self.director = dic['Director']
            self.writer = dic['Writer']
            self.actors = dic['Actors']
            self.plot = dic['Plot']
            self.language = dic['Language']
            self.country = dic['Country']
            self.poster = dic['Poster']
            self.type = dic['Type']
            self.runtime = 0
            self.rating = []  # ratings  # @ tochange
            self.averageRating = 0  # average_rating
            self.boxOffice = 0  # box_office
            self.lpmdbID = 0  # lpmdb_id

            self.setRuntime(dic['Runtime'])
            self.setRating(dic['Ratings'])
            self.setAverageRating(self.rating)
            self.setBoxOffice(dic.get('BoxOffice', 'N/A'))
            self.setlpmdbID(dic['lpmdbID'])

        else:
            self.__dict__ = dic

    def setRuntime(self, string):
        self.runtime = int(string[:-4])

    @staticmethod
    def load(dic):
        return Movie(dic, False)

    def setRating(self, list_of_ratings):

        for rating in list_of_ratings:
            if rating['Source'] == 'Internet Movie Database':
                imdb = rating['Value']
                imdb = int(imdb[:-3].replace('.',''))
                self.rating.append(imdb)
            elif rating['Source'] == 'Rotten Tomatoes':
                rotten = rating['Value']
                rotten = int(rotten[:-1])
                self.rating.append(rotten)
            elif rating['Source'] == 'Metacritic':
                metacritic = rating['Value']
                metacritic = int(metacritic[:-4])
                self.rating.append(metacritic)

    def setAverageRating(self, ratings):
        self.averageRating = sum(ratings)/len(ratings)

    def setBoxOffice(self, string):
        number = string[1:].replace(',', '')
        try:
            self.boxOffice = int(number)
        except ValueError:  # sometimes the string is 'N/A'
            self.boxOffice = 0

    def setlpmdbID(self, string):
        self.lpmdbID = int(string[2:])

    def dumps(self):
        return json.dumps(self.__dict__)
