# -*- coding: <UTF-8> -*-
import pickle as picklerick
import main_storage as ms


# make_reversed_file: String String (Movie -> list) -> None
# side effects: creates a binary reversed file with the contents of the Dict created in this function
def make_reversed_file(filepath, output_filename, λ):
    """given a filepath to the movie database file, an output filename and a function that 
    given a movie returns a list, creates a inverted file using each element of the list as 
    a index to the movie position"""
    reversed_file = {}
    flag = True
    with open(filepath, "rb") as file:
        movie = ms.readNext(file)
        while movie is not None:
            position = file.tell()
            for x in λ(movie):
                if x in reversed_file:
                    reversed_file[x].append(position)
                else:
                    reversed_file[x] = [position]
            
            movie = ms.readNext(file) # reads next iteraction movie


    print(reversed_file)
    save_reversed_file(output_filename, reversed_file)

# make_reversed_file: String Movie String (Movie -> list) -> None
# side effects: takes a binary reversed file with the name of reversed_file_path and
# adds to it the new key,value that the new movie has
def add_to_reversed_file(filepath, movie, reversed_file_path, λ):
    try:
        with open(reversed_file_path, 'rb') as file:
            reversed_file = picklerick.loads(file.read())
    except FileNotFoundError:
        print("Reversed file didn't exist: try using new_reversed_file or make_reversed_file function to create one")
        reversed_file = {}

    position = ms.getMoviePositionByID(filepath, movie['lpmdbID'])
    for x in λ(movie):
        if x in reversed_file:
            reversed_file[x].append(position)
        else:
            reversed_file[x] = list(position)
    save_reversed_file(reversed_file_path, reversed_file)
# save_reversed_file: String Dict -> None
# side effects: creates a binary reversed file with the contents of 'reversed_file'
def save_reversed_file(output_filename, reversed_file):
    """given an output filename and a reversed file, creates a binary pickled reversed_file"""
    file = open(output_filename, 'wb')
    file.write(picklerick.dumps(reversed_file))
    file.close()

# read_reversed_file: String -> Dict
def read_reversed_file(filepath):
    """recieves a path to the file, opens it and returns the reversed file dict inside of it"""
    with open(filepath, 'rb') as file:
        return picklerick.loads(file.read())

# getPositionByProperty: String String -> Integer
def getPositionByProperty(filepath, property):
    """given a path to the file and a string it constructs the dict 
    that is inside the file and returns the property field"""
    with open(filepath, 'rb') as file:
        return picklerick.loads(file.read())[property]

# new_reversed_file_multiple_elements: String String -> None
# side effect: adds all the movies in the database to the reverse file using the provided field
def new_reversed_file(database_path, field):
    """given a path to the database file and a field to access on a movie that must be a string, creates a new reversed 
    file that contains every movie in the database the movie position indexed by its field to the reverse file"""
    filepath = field + '_rf.bin'
    make_reversed_file(database_path, filepath, lambda m: str.lower(m[field]).split(', '))


# inc_reversed_file: String Movie String -> None
# side effect: adds movie to the reverse file using the provided field
def inc_reversed_file(database_path, movie, field):
    """adds the movie indexed by its field to the corresponding reversed file. It it doesn't exists it creates the first one"""
    filepath = field + '_rf.bin'
    add_to_reversed_file(database_path, movie, filepath, lambda m: str.lower(m[field]).split(', '))
