from urllib import request
import json
import time
from .movie import Movie
from ._globals import base, index_base


def http_get(query, type='i'):
    get_request = request.urlopen('http://www.omdbapi.com/?apikey=thewdb&' + type + '=' + query).read()
    return json.loads(get_request.decode())


def download_data(input_filename, output_filename):
    doAgain = True
    i = 0
    x = 0
    with open(base+output_filename, 'a') as output_file:
        output_file.write('[')

        with open(base+input_filename, 'r') as input_file:
            for IDCode in input_file:

                i += 1
                print(str(i) + ': ' + IDCode)
                # we have to do this multiple times because the website server is kinda slow
                # so timeout occurs while asking for old more unpopular movies. Our guess is
                # that they are using some variant of a splay tree because after the first
                # time we completed the get requests it was WAY faster to do it again
                while doAgain:
                    try:
                        movie_dic = http_get(IDCode)
                        doAgain = False
                        repeated = 0
                    except:
                        time.sleep(4+x)
                        x += 1 if x < 60 else -30
                        doAgain = True

                doAgain = True


                result = Movie(movie_dic)
                output_file.write(result.dumps() + ',')

    with open(base+output_filename, 'rb+') as output_file: # takes the last ',' off and puts a ']'
        output_file.seek(-1, 2)
        output_file.write(']'.encode())
