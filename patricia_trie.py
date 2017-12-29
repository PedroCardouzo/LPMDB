# -*- coding: <UTF-8> -*-
import pickle as picklerick
from main_storage import getMoviePositionByID, readNext


class PTrieNode:

    def __init__(self):
        self.key = None
        self.value = 0
        self.hasNext = False
        # 26 pointers to None for a-z, plus 10 for 0-9 plus : and ' '
        self.ptrs = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                     None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                     None, None, None, None, None, None]

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


class PatriciaTrie:

    def __init__(self):
        self.root = PTrieNode()
        self.root.value = 0

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
                        for a in range(i,j):
                            node = node.next(string[a])

                        self._insert(string, value, node, j-1)
                        node = node.next(string2[j])
                        self._insert(string2, value2, node, j)
                    else:
                        for a in range(i,j):
                            node = node.next(string[a])

                        self._insert(string, value, node.next(string[j]), j)
                        self._insert(string2, value2, node.next(string2[j]), j)
                    return

    def insert(self, movie, position=None, db_filepath='db.bin', λ=lambda x: x.title):
        position = getMoviePositionByID(db_filepath, movie.lpmdbID) if position is None else position
        self._insert(λ(movie), position)

    def save(self, filepath):
        with open(filepath, 'wb') as file:
            file.write(picklerick.dumps(self))

    @staticmethod
    def read(filepath):
        with open(filepath, 'rb') as file:
            return picklerick.loads(file.read())

    def createPatriciaTrie(self, db_filepath, pt_filepath='title_pt.bin', λ=lambda x: str.lower(x['Title'])):
        with open(db_filepath, 'rb') as file:
            position = file.tell()
            movie = readNext(file)
            while movie is not None:
                self.insert(movie, position, db_filepath, λ)
                position = file.tell()
                movie = readNext(file)

        # self.save(pt_filepath) # @ decomment

    def print(self):
        self.root._print(0)

    def searchExactMatch(self, string):
        node = self.root
        letter = iter(string)
        while node is not None and node.hasNext:
            try:
                node = node.ptrs[char_to_index(next(letter))]
            except StopIteration:
                return None

        return node.key if node is not None else None


def char_to_index(char):
    if char >= 'a':
        index = ord(char) - ord('a')
    elif char >= '0' and char <= '9':
        index = ord(char) - ord('0') + 26
    elif char == ':':
        index = -2
    else:  # char == ' '
        index = -1
    return index

ptrie = PatriciaTrie()
# ptrie.createPatriciaTrie('db.bin')
ptrie.print()
x = 0
lista = [('aaa', x), ('aaba', x), ('chac', x), ('dhad', x), ('lord of the rings', x), ('lord of the rings the comeback', x)]
for s,v in lista:
    ptrie._insert(s, v+x)
    x += 10
ptrie.print()

# print(rt.ptrs[char_to_index('h')].ptrs[(char_to_index('a'))].ptrs)
# print(rt.ptrs[char_to_index('a')].ptrs[char_to_index('a')].ptrs[char_to_index('b')].key)#.ptrs[char_to_index('a')].key)
print(ptrie.searchExactMatch('aa'))
ptrie.save('ptrie_test.bin')
pt = PatriciaTrie.read('ptrie_test.bin')
print('printing pt')
pt.print()
