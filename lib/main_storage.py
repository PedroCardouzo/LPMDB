import pickle as picklerick
from struct import pack, unpack
from bisect import bisect, insort
from collections import namedtuple
from .movie import Movie
from ._globals import base
import json


id_index = namedtuple('id_index', 'lpmdbID, address')


# getElementSize: FILE* -> Integer
def getElementSize(file):
    """recieves a file pointer and reads from it the next 4 bytes that should be a little endian integer
     that informs the size in bytes of the variable sized object that is stores as a byte array there.
     It then converts the 4 bytes read to a little endian integer and returns it"""
    size = file.read(4) # int size = 4
    return unpack('<i', size)[0] # '<i' -> little endian integer
    # unpack returns a tuple, even if it is only one element


# storeElementSize: FILE* bytes -> Integer
def storeElementSize(file, element):
    """recieves a file pointer and a bytes object and store the
    length of the byte array as a 4 bytes little endian integer
    returns the number of bytes stored (should be 4)"""
    element_size = pack('<i', len(element))
    return file.write(element_size)


# printDB: String -> None
# side effect: prints the whole db
def printDB(database_filename, f=None):
    with open(base+database_filename, 'rb') as file:
        pos = file.tell()
        movie = readNext(file)
        while movie is not None:
            print(movie.title + ' @ ' + str(pos))
            if f is not None:
                print(f(movie))

            pos = file.tell()
            movie = readNext(file)


# readNext: FILE* -> ANY
def readNext(file):
    """recieves a file pointer, reads first 4 bytes from a file and converts it into a little endian integer then it
    takes that integer's value (let's suppose x = 102) and reads the next x = 102 bytes from the file. It then
    unpickles it and returns the object in its original form. If EOF was reached, it returns None"""
    try:
        size = getElementSize(file)
    except:
        return None
    byte_array = file.read(size)
    return picklerick.loads(byte_array)


# readMovieByPos: String Integer ->  ANY
def readMovieByPos(filepath, position):
    """recieves a string (filepath) and a position (integer) opens the file pointed by filepath and seeks the position 'position'"""
    with open(base+filepath, 'rb') as file:
        file.seek(position)
        return readNext(file)


# getMoviePositionByID: String Integer -> Integer or None
def getMoviePositionByID(filepath, id):
    """given a filepath and an id, loads the movie with that id form the file that filepath points to.
    If the movie isn't in the database returns None"""
    index_filepath = filepath.split('.')[0] + '.lpmdb'
    with open(base+index_filepath, 'rb') as index_file:
        index_table = picklerick.loads(index_file.read())
        # -1 is used because after sorting from first argument,
        # if found any equal it will sort by the second argument
        pos = bisect(index_table, (id, -1))
        value = index_table[pos]

        if value.lpmdbID == id:
            return value.address
        else:
            return None


# index_position: (String || FILE*) Integer Integer [Boolean]-> None
def index_position(filepath, key, value, keep_open=False):
    """recieves a string and and 2 integers. Then it opens a file with that name, which is a indexing file.
    It inserts the key, value pair at the correct position so that it is still sorted by lpmdbID"""
    table_value = id_index(key, value)

    if type(filepath) is str:
        try:
            file = open(base+filepath, 'rb+')
        except FileNotFoundError:
            open(base+filepath, 'wb').close()
            file = open(base+filepath, 'rb+')
    else:
        file = filepath

    try:
        index_table = picklerick.loads(file.read())
        insort(index_table, table_value)
    except EOFError:
        index_table = [table_value]

    bytes_array = picklerick.dumps(index_table)
    del index_table
    file.seek(0)
    file.write(bytes_array)

    if not keep_open:
        file.close()


def json_to_lpmdb_bin(source_file, dest_file):
    with open(base + source_file, 'r') as file:
        dict_list = json.loads(file.read())

    with open(base + dest_file, 'ab') as file:
        for d in dict_list:
            writeAppend(file, Movie.load(d), keep_open=True)


# writeAppend: (String || FILE*) Movie [Boolean FILE*] -> Integer
def writeAppend(filepath, movie_object, keep_open=False):
    """Recieves a string that is the path to the file (or the file itself) and an arbitrary object. It then opens the file as append binary,
    pickles the object to transform it into a bytes array. Then it uses file.tell() to get the position where the
    new object will be inserted and stores it in a variable 'pos'. It proceeds to store the length of the bytes
    array as a little endian integer and then writes the bytes array to the file. After that it saves the
    value of 'pos' in a indexing file with the same filepath, but ending in '.lpmdb' using lpmdbID as keys.
    At the end returns the position where the movie is at the main DB file"""
    lpmdbID = movie_object.lpmdb_id
    if type(filepath) is str:
        file = open(base+filepath, 'ab')
    else:
        file = filepath
        filepath = filepath.name

    index_filepath = filepath.split('.')[0] + '.lpmdb'

    byte_array = picklerick.dumps(movie_object)
    pos = file.tell()
    # print('position @ ' + str(pos))  # @ debug
    storeElementSize(file, byte_array)
    file.write(byte_array)
    
    index_position(index_filepath, lpmdbID, pos)

    if not keep_open:
        file.close()

    return pos


def dumpMultipleMovies(filepath, list_of_movies):
    with open(base+filepath, 'ab') as file:
        for movie in list_of_movies:
            writeAppend(file, movie, keep_open=True)


# populate: list -> list
def populate(list_of_addresses, filename='lpmdb.bin'):
    """given a list of addresses, it populates the list with the contents of the addresses"""
    return [readMovieByPos(filename, x) for x in list_of_addresses]