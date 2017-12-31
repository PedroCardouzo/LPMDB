# -*- coding: <UTF-8> -*-
import pickle as picklerick
import lib.main_storage as ms
from ._globals import base, index_base


class PTrieNode:

    def __init__(self):
        self.key = None
        self.value = 0
        self.hasNext = False
        # 26 pointers to None for a-z, plus 10 for 0-9 plus : and ' '
        self.ptrs = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                     None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                     None, None, None, None, None, None, None, None, None, None, None, None, None]


    def next(self, char):
        self.hasNext = True

        index = char_to_index(char)

        if self.ptrs[index] is None:
            self.ptrs[index] = PTrieNode()

        return self.ptrs[index]

    def set(self, string, value):
        self.key = string
        self.value = value

    def _print(self, level):
        print('key=' + str(self.key) + ', value=' + str(self.value) + ', lvl=' + str(level))
        for x in self.ptrs:
            if x is not None:
                x._print(level+1)

    def extract(self):
        out = []
        if self.key is not None:
            out.append((self.key, self.value))
        for node in self.ptrs:
            if node is not None:
                out += node.extract()
        return out

class PatriciaTrie:

    def __init__(self):
        self.root = PTrieNode()
        self.root.value = 0

    @staticmethod
    def propagate_to_branches(node_list):
        out = []
        for node in node_list:
                out += node.extract()
        return out

    def _insert(self, string, value, node=None, start_ind=0):
        node = self.root if node is None else node
        for i in range(start_ind, len(string)):
            if node.key is None:
                if node.hasNext:
                    node = node.next(string[i])
                else:
                    node.set(string, value)
                    return
            else:
                if len(node.key) == i:
                    node = node.next(string[i])
                else:
                    string2 = node.key
                    value2 = node.value
                    if string == string2:
                        print('register with key=' + string2 + ' already exists')
                    else:
                        node.key, node.value = None, 0
                        j = 0
                        for c1, c2 in zip(string, string2):
                            if c1 == c2:
                                j += 1
                            else:
                                break
                        if j == len(string2):
                            string, string2 = string2, string
                            value, value2 = value2, value
                        if j == len(string):  # in case one string is the prefix of the other
                            for a in range(i, j):
                                node = node.next(string[a])
                            self._insert(string, value, node, j-1)

                            node = node.next(string2[j])
                            self._insert(string2, value2, node, j)
                        else:
                            for a in range(i, j):
                                node = node.next(string[a])

                            self._insert(string, value, node.next(string[j]), j)
                            self._insert(string2, value2, node.next(string2[j]), j)
                        return
        node.set(string, value)  # got to the end of the string, so it belongs to this node
        return

    def insert(self, movie, position=None, db_filepath='lpmdb.bin', λ=lambda x: x.title):
        position = ms.getMoviePositionByID(db_filepath, movie.lpmdb_id) if position is None else position
        self._insert(λ(movie), position)

    def save(self, filepath, is_filepath=False):
        """saves the patricia trie to the database. It assumes the filepath recieved is actually a field name and
        saves the file with a special name derived from it. If is_filepath=True, it doesn't do that conversion"""
        if not is_filepath:
            filepath += '_ptrie.bin'
        with open(index_base+filepath, 'wb') as file:
            file.write(picklerick.dumps(self))

    @classmethod
    def load(cls, field, suffix=False):
        """given a field, converts it to the equivalent filename and opens it"""
        extra = '_suf' if suffix else ''
        return cls.read(field+extra+'_ptrie.bin')

    @staticmethod
    def read(filepath):
        try:
            with open(index_base+filepath, 'rb') as file:
                return picklerick.loads(file.read())
        except FileNotFoundError:
            return None
    @staticmethod
    def create_patricia_trie(db_filename, λ=lambda mv: mv.title.lower()):
        pt = PatriciaTrie()
        pt._createPatriciaTrie(db_filename, λ)
        return pt

    def _createPatriciaTrie(self, db_filename, λ):
        with open(base+db_filename, 'rb') as file:
            position = file.tell()
            movie = ms.readNext(file)
            while movie is not None:
                self.insert(movie, position, db_filename, λ)
                position = file.tell()
                movie = ms.readNext(file)


    def print(self):
        self.root._print(0)

    def searchExactMatch(self, string):
        node = self.root
        for letter in string:
            if node.hasNext:
                node = node.next(letter)
            else:
                break

        return node.key,node.value if node is not None else None

    def prefixSearch(self, string):
        node = self.root
        for letter in string:
            if node is not None and node.hasNext:
                node = node.ptrs[char_to_index(letter)]
            else:
                break
        return [node]

    def _infixSearch(self, infix, _i, node):
        out = []
        if node is None:
            return []
        else:
            if _i == len(infix):
                return [node]
            elif node.hasNext:
                if node.key == "caacbo":
                    print(node.key)
                    print(_i)
                index = char_to_index(infix[_i])
                index_str0 = char_to_index(infix[0])

                for i, _node in enumerate(node.ptrs):
                    if _node is not None:
                        if i == index:
                            out += self._infixSearch(infix, _i+1, _node)
                        elif i == index_str0:
                            out += self._infixSearch(infix, 1, _node)
                        else:
                            out += self._infixSearch(infix, 0, _node)
                return out

            elif infix in node.key:
                return [node]
            else:
                return []


    def infixSearch(self, infix):
        return self._infixSearch(infix, 0, self.root)

    def testFill(self, lista):
        x = 0
        for s in lista:
            ptrie._insert(s, x)
            x += 10


def char_to_index(char):
    if char >= 'a':
        index = ord(char) - ord('a')
    elif char >= '0' and char <= '9':
        index = ord(char) - ord('0') + 26
    elif char == ':':
        index = -6
    elif char == '.':
        index = -5
    elif char == ',':
        index = -4
    elif char == "'":
        index = -3
    elif char == ' ':  # char == ' '
        index = -2
    else:
        index = -1
        print('unindentified char: ' + char)
    return index


# @ test

# ptrie = PatriciaTrie()
# ptrie.createPatriciaTrie('db.bin')
# x = 0
# lista = ['caca', 'macarroni', 'acbolado', 'acb', 'acd', 'caacbo', 'ccaa']
# lista = ['ar', 'args']
# ptrie.testFill(lista)
# ptrie.print()
# print(ptrie.root.ptrs[char_to_index('a')].ptrs[(char_to_index('g'))].ptrs[(char_to_index('o'))].key)
# print(rt.ptrs[char_to_index('a')].ptrs[char_to_index('a')].ptrs[char_to_index('b')].key)#.ptrs[char_to_index('a')].key)
# ptrie.print()
# print(ptrie.searchExactMatch('agon'))
# print(ptrie.prefixSearch('ab')[0].ptrs[char_to_index('b')].key)
# l = ptrie.infixSearch('cb')
# print(l)
# print(l[0].ptrs[1].key)
# print(l[0].ptrs[3].key)
# print(l[0].key)
# print(l[0].ptrs[char_to_index('o')].key)
# print(l[1].key)

# a = ptrie.genericSearch('wi', ptrie.infixSearch)
# print(len(a))