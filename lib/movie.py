import json
import locale


locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class Movie:

    def __init__(self, dic, transform=True):
        if transform:
            # all fields are declared here, although they may change value
            self.title = dic['Title']
            self.year = int(dic['Year'][:4])
            self.rated = dic['Rated']
            self.genre = dic['Genre']
            self.director = dic['Director']
            self.writer = dic['Writer']
            self.actors = dic['Actors']
            self.plot = dic['Plot']
            self.language = dic['Language']
            self.country = dic['Country']
            self.awards = dic['Awards']
            self.poster = dic['Poster']
            self.type = dic['Type']
            self.runtime = 0
            self.ratings = []
            self.average_rating = 0
            self.box_office = 0
            self.lpmdb_id = 0

            self.setRuntime(dic['Runtime'])
            self.setRatings(dic['Ratings'])
            self.setAverageRating()
            self.setBoxOffice(dic.get('BoxOffice', 'N/A'))
            self.setlpmdbID(dic['imdbID'])

        else:
            self.__dict__ = dic

    def __str__(self):
        return ("Title: {}\n".format(self.title)
                + "Year: {}\n".format(self.year)
                + "Rated: {}\n".format(self.rated)
                + "Genre: {}\n".format(self.genre)
                + "Director: {}\n".format(self.director)
                + "Writer: {}\n".format(self.writer)
                + "Actors: {}\n".format(self.actors)
                + "Plot: {}\n".format(self.plot)
                + "Language: {}\n".format(self.language)
                + "Country: {}\n".format(self.country)
                + "Awards: {}\n".format(self.awards)
                + "Poster: {}\n".format(self.poster)
                + "Type: {}\n".format(self.type)
                + "Runtime: {} min\n".format(self.runtime)
                + "Ratings: {}\n".format(self.print_ratings())
                + "Average Rating: {}\n".format(self.average_rating)
                + "Box Office: {}\n".format(locale.currency(self.box_office, grouping=True))
                + "lpmdbID: {}\n".format(self.lpmdb_id))

    def print_ratings(self):
        out = '[Internet Movie Database: {}, Rotten Tomatoes: {}, Metacritic: {}]'
        out = out.format(*self.ratings)
        return out

    def setRuntime(self, string):
        self.runtime = int(string[:-4])

    @staticmethod
    def load(dic):
        return Movie(dic, False)

    def setRatings(self, list_of_ratings):

        for rating in list_of_ratings:
            if rating['Source'] == 'Internet Movie Database':
                imdb = rating['Value']
                imdb = int(imdb[:-3].replace('.',''))
                self.ratings.append(imdb)
            elif rating['Source'] == 'Rotten Tomatoes':
                rotten = rating['Value']
                rotten = int(rotten[:-1])
                self.ratings.append(rotten)
            elif rating['Source'] == 'Metacritic':
                metacritic = rating['Value']
                metacritic = int(metacritic[:-4])
                self.ratings.append(metacritic)

    def setAverageRating(self):
        self.average_rating = sum(self.ratings)/len(self.ratings)

    def setBoxOffice(self, string):
        number = string[1:].replace(',', '')
        try:
            self.box_office = int(number)
        except ValueError:  # sometimes the string is 'N/A'
            self.box_office = 0

    def setlpmdbID(self, string):
        self.lpmdb_id = int(string[2:])

    def dumps(self):
        return json.dumps(self.__dict__)
