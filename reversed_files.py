# -*- coding: <UTF-8> -*-
import pickle as picklerick

def readMovie(file):
    return file
    # n_bytes = file.read(size(int))
    # data = file.read(n_bytes)
    # picklerick.pickle(data)

def make_reversed_file(filename, output_filename, λ):
	reversed_file = {}
	with open(filename, "rb") as file:
		while not end of file:
			movie = readMovie(file)
			for x in λ(movie):
				if x in reversed_file:
					reversed_file[x].append(file.tell())
				else:
					reversed_file[x] = list(file.tell())



		save reversed_file