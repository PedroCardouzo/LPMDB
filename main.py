from lib.parser import Parser
from lib.patricia_trie import PatriciaTrie
import lib.main_storage as ms
from lib.data_fetcher import download_data

def main():
    # parser = Parser()

    # download_data('IDs.txt', '___new_lpmdb.json')  # will fetch data to a new file (this name as one _ more at the beggining)

    # ms.printDB('lpmdb.bin', f=lambda x: x.released)
    # parser.parse(':: from title filter the as dft')
    # while parser.parse(input()):  # returns false if input() returns "exit"
    #     pass

    # parser.parse('make ptrie lpmdb.bin')


if __name__ == '__main__':
    main()
