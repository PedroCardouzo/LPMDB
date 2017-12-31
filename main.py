from lib.parser import Parser
from lib.patricia_trie import PatriciaTrie
import lib.main_storage as ms

def main():
    parser = Parser()

    # ms.printDB('lpmdb.bin', f=lambda x: x.released)
    parser.parse(':: from title filter the as dft')
    while parser.parse(input()):  # returns false if input() returns "exit"
        pass

    # parser.parse('make ptrie lpmdb.bin')


if __name__ == '__main__':
    main()
