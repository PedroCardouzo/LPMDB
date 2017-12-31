# patricia trie tests:
# delete all files and paste this in main ->

# ms.json_to_lpmdb_bin('sample.json', 'lpmdb.bin')  # <- RUN ONE TIME ONLY

# with open(base+'lpmdb.bin', 'rb') as file:
#     a = ms.readNext(file)
#     while a is not None:
#         print(a.title)
#         a = ms.readNext(file)


# download_data('IDs.txt', '___new_lpmdb.json')  # will fetch data to a new file (this name as one _ more at the beggining)

# pt = PatriciaTrie.create_patricia_trie('lpmdb.bin', 'title')
# pt.save('title')
# del pt
pt = PatriciaTrie.load('title')
# pt.print()
l = ["The Fifth Element",
     "Liar Liar",
     "The Lost World: Jurassic Park",
     "Men in Black",
     "The Fast and the Furious",
     "Jurassic Park III",
     "Ocean's Eleven",
     "Shrek",
     "8 Mile",
     "The Bourne Identity",
     "Harry Potter and the Chamber of Secrets",
     "School of Rock",
     "X-Men 2",
     "Cheaper by the Dozen",
     "Matrix Revolutions",
     "Mystic River",
     "The Bourne Supremacy",
     "The Butterfly Effect",
     "I, Robot",
     "Kill Bill: Vol. 2"]
# for s in l:
#     print(pt.infixSearch(str.lower(s[1:-2]))[0].value)
# mv = ms.readMovieByPos('lpmdb.bin', 16896)
# print(mv.title)
mvs = pt.infixSearch('the')
aux = []
# does wildcard searches: equivalent to "*the*supremacy*"
for node in mvs:
    aux += pt._infixSearch('supremacy', 0, node)

print(PatriciaTrie.propagate_to_branches(aux))

# reversed files tests:
# delete all files and paste this in main ->

# ms.json_to_lpmdb_bin('sample.json', 'lpmdb.bin')  # <- RUN ONE TIME ONLY

# with open(base+'lpmdb.bin', 'rb') as file:
#     a = ms.readNext(file)
#     while a is not None:
#         print(a.title)
#         a = ms.readNext(file)

# rf.new_reversed_file('lpmdb.bin', 'genre')
rev_file = rf.read('genre')
print(rev_file)
print('size of reverse dict: ' + str(len(picklerick.dumps(rev_file))) + ' bytes')
mv = ms.readMovieByPos('lpmdb.bin', rev_file['animation'][0])
print(mv.title)


# BTree tests:
# delete all files and paste this in main ->

# ms.json_to_lpmdb_bin('sample.json', 'lpmdb.bin')  # <- RUN ONE TIME ONLY

# with open(base+'lpmdb.bin', 'rb') as file:
#     a = ms.readNext(file)
#     while a is not None:
#         print(a.title)
#         a = ms.readNext(file)

bt = BTree.createBTree('lpmdb.bin', 2)
bt.print()
del bt
bt = bt.load('averageRating')  # @ tochange
res = bt.search(le, 65)
print(res)
for el in res:
     movie = ms.readMovieByPos('lpmdb.bin', el.value)
     print(movie.title)
     print(movie.averageRating)
     print(movie.rating)

# BTree in cmd
     parser = Parser()

     parser.parse(':: 65 > averageRating > 40 as dft')

     # print(parser.names)
     print([x.title for x in parser.names['dft']])

# rf is working in cmd


# piping filter is working in cmd
    parser = Parser()

    parser.parse(':: 65 > averageRating > 40 as dft | title jurassic ')

    # print(parser.names)
    print([x.title for x in parser.names['dft']])


    # MULTIPLE FILTERS TOO!
    parser = Parser()

    parser.parse(':: 65 > averageRating > 40 as dft | title jurassic | released > 2000')  # RELEASED MAY CHANGE TO YEAR

    # print(parser.names)
    print([(x.title, x.released) for x in parser.names['dft']])

# patricia tree parser IS OK TOO :D

        parser = Parser()
        #
        parser.parse(':: from title match 2 | released > 2003 | title 2')

        # print(parser.names)
        print([(x.title, x.released) for x in parser.names['default']])
