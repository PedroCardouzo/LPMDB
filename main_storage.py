import pickle as picklerick
from struct import pack, unpack
from bisect import bisect, insort
from collections import namedtuple

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
    with open(filepath, 'rb') as file:
        file.seek(position)
        return readNext(file)

# getMoviePositionByID: String Integer -> Integer or None
def getMoviePositionByID(filepath, id):
    """given a filepath and an id, loads the movie with that id form the file that filepath points to.
    If the movie isn't in the database returns None"""
    index_filepath = filepath.split('.')[0] + '.lpmdb'
    with open(index_filepath, 'rb') as index_file:
        index_table = picklerick.loads(index_file.read())
        # -1 is used because after sorting from first argument, 
        # if found any equal it will sort by the second argument
        pos = bisect(index_table, (id,-1)) 
        value = index_table[pos]
        del index_table
        if value.lpmdbID == id:
            return value.address
        else:
            return None

# index_position: (String || FILE*) Integer Integer [Boolean]-> None
def index_position(filepath, key, value, keep_open=False):
    """recieves a string and and 2 integers. Then it opens a file with that name, which is a indexing file. It inserts the key,value pair at the correct position
     so that it is still sorted by lpmdbID"""
    table_value = id_index(key,value)

    if type(filepath) is str:
        try:
            file = open(filepath, 'rb+')
        except FileNotFoundError:
            open(filepath, 'wb').close()
            file = open(filepath, 'rb+')
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


# writeAppend: (String || FILE*) Movie [Boolean FILE*] -> None
def writeAppend(filepath, movie_object, keep_open=False):
    """Recieves a string that is the path to the file (or the file itself) and an arbitrary object. It then opens the file as append binary,
    pickles the object to transform it into a bytes array. Then it uses file.tell() to get the position where the
    new object will be inserted and stores it in a variable 'pos'. It proceeds to store the length of the bytes
    array as a little endian integer and then writes the bytes array to the file. After that it saves the
    value of 'pos' in a indexing file with the same filepath, but ending in '.lpmdb' using lpmdbID as keys."""
    lpmdbID = int(movie_object['lpmdbID']) # @change remove int() cast
    if type(filepath) is str:
        file = open(filepath, 'ab')
    else:
        file = filepath
        filepath = filepath.name

    index_filepath = filepath.split('.')[0] + '.lpmdb'

    byte_array = picklerick.dumps(movie_object)
    pos = file.tell()
    storeElementSize(file, byte_array)
    file.write(byte_array)
    
    index_position(index_filepath, lpmdbID, pos)

    if not keep_open:
        file.close()

def dumpMultipleMovies(filepath, list_of_movies):
    with open(filepath, 'ab') as file:
        for movie in list_of_movies:
            writeAppend(file, movie, keep_open = True)
