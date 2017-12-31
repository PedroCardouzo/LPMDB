from lib.parser import Parser
from lib.patricia_trie import PatriciaTrie
import lib.main_storage as ms
from lib.data_fetcher import download_data

def main():
    parser = Parser()


    # ms.printDB('lpmdb.bin')
    # ms.json_to_lpmdb_bin('lpmdb.json', 'lpmdb.bin')
    # mv = ms.readMovieByPos('lpmdb.bin', 11616)
    # print(mv.title)

    # parser.parse(':: from title filter the')
    while parser.parse(input()):  # returns false if input() returns "exit"
        pass

    # parser.parse('make ptrie lpmdb.bin')


if __name__ == '__main__':
    main()
