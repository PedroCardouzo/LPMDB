from operator import gt, ge, lt, le, eq
from bisect import bisect
from collections import namedtuple
from ._globals import base, index_base


BTreeNodeElement = namedtuple("BTreeNodeElement", "key, value, child")


class BTreeNode:
    def __init__(self, elements, greater, leaf=False):
        self.elements = elements
        self.nKeys = len(elements)
        self.greater = greater
        self.leaf = leaf

    def __len__(self):
        return len(self.elements)

    def _print(self, level):
        if self.leaf:
            for el in self.elements:
                print(str(el.key) + ' - lvl: ' + str(level))
        else:
            for el in self.elements:
                el.child._print(level+1)
                print(str(el.key) + ' - lvl: ' + str(level))
            try:
                self.greater._print(level+1)
            except AttributeError:
                print([x.key for x in self.elements])
                print(self.greater)

    def removeRange(self, upto_index, from_index=0):
        """Recieves two numbers and removes from node every element from the second number
           (default zero) up to first number (including it).
           After removing the elements it updates the nKeys field
        """
        for _ in range(from_index, upto_index+1):
            del self.elements[0]

        self.nKeys = len(self.elements)

    def insert(self, index, x):
        self.elements.insert(index, x)
        self.nKeys += 1

    def search(self, cf, tv, out):
        if type(self) is BTreeNode:
            
            t_out = [x for x in self.elements if cf(x.key, tv)]
            ind = len(t_out)
            if self.leaf:
                out += t_out
            else:
                
                if cf == eq:
                    ind = bisect([x.key for x in self.elements], tv)
                
                doGreater = cf == gt or cf == ge or ind >= self.nKeys

                # in final implementation it may not be from i=0 to ind-1 because filtered elements may not start at i = 0
                # (i.e. if there is a node list and a child list, one independent from the other)
                # can solve this with indexing = range(len(btn.nodes)) when generating t_out so that you generate a
                # tuple/namedtuple with [(i,x) for i,x in btn.nodes if cf(x.key, tv)]
                for x in t_out:
                    x.child.search(cf, tv, out)
                    out.append(x)
                del t_out
                if doGreater:
                    self.greater.search(cf, tv, out)
                else:
                    self.elements[ind].child.search(cf, tv, out)


class BTree:
    def __init__(self, t):
        self.root = []
        self.min = t-1
        self.max = 2*t-1

    # insert: BTree BTreeNodeElement -> None
    # recieves self and a BTreeNodeElement and inserts it into the BTree
    def insert(self, x):
        inserted, overflow = False, False
        node = self.root
        visited = []
        if self.root == []:
            self.root = BTreeNode(
                            [BTreeNodeElement(
                                    x.key,
                                    x.value,
                                    []
                            )],
                            [],
                            True
                        )
            inserted = True
        while not inserted:
            keys = [el.key for el in node.elements]
            i = bisect(keys, x.key)
            if overflow:
                if node.nKeys < self.max:
                    node.insert(i, x)
                    inserted = True
                elif visited == []:
                    node.insert(i, x)
                    med = int(len(node)/2)
                    median = node.elements[med]
                    self.root = BTreeNode(
                                    [BTreeNodeElement(
                                        median.key,
                                        median.value,
                                        BTreeNode(
                                            node.elements[:med],
                                            median.child,
                                            node.leaf
                                        )
                                    )],
                                    node
                                )
                    node.removeRange(med)
                    inserted = True
                else:
                    node.insert(i, x)
                    med = int(len(node)/2)
                    median = node.elements[med]
                    x = BTreeNodeElement(
                        median.key,
                        median.value,
                        BTreeNode(
                            node.elements[:med],
                            median.child,
                            node.leaf
                        )
                    )
                    node.removeRange(med)
                    node = visited.pop()

            elif not node.leaf:
                visited.append(node)
                if i == node.nKeys:
                    node = node.greater
                else:
                    node = node.elements[i].child
            else: # if node is leaf
                if node.nKeys < self.max:
                    node.insert(i, x)
                    inserted = True
                else:
                    overflow = True

    def print(self):
        self.root._print(0)

    @staticmethod
    def load(filename):
        with open(index_base + filename, 'rb') as file:
            return picklerick.loads(file.read())

    def save(self, filename):
        with open(index_base + filename, 'wb') as file:
            return file.write(picklerick.dumps(self))

    def search(self, cf, tv):
        out = []
        self.root.search(cf, tv, out)
        return out

# pseudoBTree = BTreeNode([
#                   Value(2.8, BTreeNode([
#                                 Value(2.7, None),
#                                 Value(2.8, None)
#                              ])
#                   ),
#                   Value(3.5, BTreeNode([next(letter)
#                                 Value(2.9, None),
#                                 Value(3.4, None)
#                              ])
#                   ),
#                   Value(4.4, BTreeNode([
#                                 Value(4.1, BTreeNode([Value(3.9, None), Value(4.0, None)])),
#                                 Value(4.3, None)
#                              ])
#                   )
#               ])
#
# pseudoBTree.insertGreater(BTreeNode([Value(4.5, None), Value(4.9, None)]))
# pseudoBTree.nKeys = 2

# makeNodeElement: Number ANY -> BTreeNodeElement
def makeNodeElement(key, value):
    return BTreeNodeElement(key, value, [])

# @ test
# bt = BTree(2)

# keys = [3.2, 3.6, 2.6, 4.5, 3.3, 4.9, 4.6, 3.5, 1.4, 4.2, 4.7, 4.8, 5.0, 5.0, 5.0, 5.0, 0.7, 0.9, 4.9]
# gen = (x for x in range(100))
# elements = [makeNodeElement(x, next(gen)) for x in keys]


# for element in elements:
#     bt.insert(element)

# print('insertion over:')


# bt.print()

# cf = eq
# tv = 5

# output = bt.search(cf, tv)

# output = [(x.key, x.value) for x in output]
# keys = [x for x in keys if cf(x, tv)]

# print(output)
# print(keys)

# # checks if lists are equal
# for el in output:
#     keys.remove(el[0])
# print(keys == [])