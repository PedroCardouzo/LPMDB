# patricia trie tests:
# delete all files and paste this in main
# ms.json_to_lpmdb_bin('sample.json', 'lpmdb.bin')

# with open(base+'lpmdb.bin', 'rb') as file:
#     a = ms.readNext(file)
#     while a is not None:
#         print(a.title)
#         a = ms.readNext(file)

pt = PatriciaTrie.create_patricia_trie('lpmdb.bin', 'ptrie_title.bin')
pt.save('ptrie_title.bin')
del pt
pt = PatriciaTrie.read('ptrie_title.bin')
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
for s in l:
    print(pt.infixSearch(str.lower(s[1:-2]))[0].value)
mv = ms.readMovieByPos('lpmdb.bin', 16896)
print(mv.title)

#