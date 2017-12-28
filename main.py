import main_storage as ms
import reversed_files
import btree as BTree


def test():
	reversed_files.make_reversed_file('db.bin', 'genre_rf.bin', lambda m: str.lower(m['Genre']).split(', '))