import pickle as picklerick
from struct import pack, unpack
from bisect import bisect, insort

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
    unpickles it and returns the object in its original form"""
    size = getElementSize(file)
    byte_array = file.read(size)
    return picklerick.loads(byte_array)

# getMovieByID: String Integer -> ANY
def getMovieByID(filepath, id):
    """given a filepath and an id, loads the movie with that id form the file that filepath points to
    if the movie isn't in the database returns -1"""
    index_filepath = filepath.split('.')[0] + '.lpmdb'
    with open(index_filepath, 'rb') as index_file:
        index_table = picklerick.loads(file.read())
        pos = bisect(index_table, (id,None))-1
        del index_table
    with open(filepath, 'rb') as file:
        fseek(pos)
        value = readNext(file)
        if value.lpmdbID == id:
            return value
        else
            return None

# index_position: String Integer Integer -> None
def index_position(filepath, key, value):
    """recieves a string and and 2 integers. It splits the string at the first '.' and appends '.lpmdb' there.
    Then it opens a file with that name, which is a indexing file. It inserts the key,value pair at the correct position
     so that it is still sorted by lpmdbID"""
    filepath = filepath.split('.')[0] + '.lpmdb'
    table_value = id_index(key,value)
    with open(filepath, 'wb+') as file:
        index_table = picklerick.loads(file.read())
        insort(index_table, table_value)
        bytes_array = picklerick.dumps(index_table)
        del index_table
        file.seek(0)
        file.write(bytes_array)


# writeAppend: String ANY -> None
def writeAppend(filepath, any_object):
    """Recieves a string that is the path to the file and an arbitrary object. It then opens the file as append binary,
    pickles the object to transform it into a bytes array. Then it uses file.tell() to get the position where the
    new object will be inserted and stores it in a variable 'x'. It proceeds to store the length of the bytes
    array as a little endian integer and then writes the bytes array to the file. After that it saves the
    value of 'x' in a indexing file with the same filepath, but ending in '.lpmdb' using lpmdbID as keys."""
    lpmdbID = any_object['lpmdbID']
    with open(filepath, 'ab') as file:
        byte_array = picklerick.dumps(any_object)
        x = file.tell()
        storeElementSize(file, byte_array)
        file.write(byte_array)
    index_position(filepath, lpmdbID, x)