import lib.main_storage as ms
from operator import gt, ge, lt, le, eq
import lib.reversed_files as rf
from lib.btree import BTree
from lib.patricia_trie import PatriciaTrie
from lib._globals import base, index_base
import pickle as picklerick

def main():
    # ms.json_to_lpmdb_bin('sample.json', 'lpmdb.bin')

    # with open(base+'lpmdb.bin', 'rb') as file:
    #     a = ms.readNext(file)
    #     while a is not None:
    #         print(a.title)
    #         a = ms.readNext(file)

    bt = BTree.createBTree(2, 'lpmdb.bin')
    bt.print()
    res = bt.search(le, 65)
    print(res)
    for el in res:
        movie = ms.readMovieByPos('lpmdb.bin', el.value)
        print(movie.title)
        print(movie.averageRating)
        print(movie.rating)

main()