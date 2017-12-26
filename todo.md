makeInvertedFile: String String (Movie -> list) -> None

Recieves a filename with all movies, an output filename and a function that given a movie, returns a list of strings where the values are
the keys we want to add the movie in the inverted file. It then proceeds to add the movie in the proper field of the inverted file

example:

file -> [
# position 0 ->
	{"Title":"Fake Harry Potter where Alan Howard appeared","Year":"2011","Rated":"PG-13","Released":"15 Jul 2011","Runtime":"130 min","Genre":"Adventure, Drama, Fantasy","Director":"David Yates","Writer":"Steve Kloves (screenplay), J.K. Rowling (novel)","Actors":"Ralph Fiennes, Michael Gambon, Alan Rickman, Alan Howard, Daniel Radcliffe","Plot":"Harry, Ron, and Hermione search for Voldemort's remaining Horcruxes in their effort to destroy the Dark Lord as the final battle rages on at Hogwarts.","Language":"English","Country":"USA, UK","Awards":"Nominated for 3 Oscars. Another 45 wins & 92 nominations.","Poster":"https://images-na.ssl-images-amazon.com/images/M/MV5BMjIyZGU4YzUtNDkzYi00ZDRhLTljYzctYTMxMDQ4M2E0Y2YxXkEyXkFqcGdeQXVyNTIzOTk5ODM@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie Database","Value":"8.1/10"},{"Source":"Rotten Tomatoes","Value":"96%"},{"Source":"Metacritic","Value":"87/100"}],"Metascore":"87","imdbRating":"8.1","imdbVotes":"615,742","imdbID":"tt1201607","Type":"movie","DVD":"11 Nov 2011","BoxOffice":"$381,000,185","Production":"Warner Bros. Pictures","Website":"http://www.HarryPotter.com/","Response":"True"},
# position 136 ->
	{"Title":"The Lord of the Rings: The Fellowship of the Ring","Year":"2001","Rated":"PG-13","Released":"19 Dec 2001","Runtime":"178 min","Genre":"Adventure, Drama, Fantasy","Director":"Peter Jackson","Writer":"J.R.R. Tolkien (novel), Fran Walsh (screenplay), Philippa Boyens (screenplay), Peter Jackson (screenplay)","Actors":"Alan Howard, Noel Appleby, Sean Astin, Sala Baker","Plot":"A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle Earth from the Dark Lord Sauron.","Language":"English, Sindarin","Country":"New Zealand, USA","Awards":"Won 4 Oscars. Another 113 wins & 124 nominations.","Poster":"https://images-na.ssl-images-amazon.com/images/M/MV5BN2EyZjM3NzUtNWUzMi00MTgxLWI0NTctMzY4M2VlOTdjZWRiXkEyXkFqcGdeQXVyNDUzOTQ5MjY@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie Database","Value":"8.8/10"},{"Source":"Rotten Tomatoes","Value":"91%"},{"Source":"Metacritic","Value":"92/100"}],"Metascore":"92","imdbRating":"8.8","imdbVotes":"1,364,895","imdbID":"tt0120737","Type":"movie","DVD":"06 Aug 2002","BoxOffice":"$314,000,000","Production":"New Line Cinema","Website":"http://www.lordoftherings.net/film/trilogy/thefellowship.html","Response":"True"}
]

output filename -> whatever

function -> lambda x: x.Actors

Ralph Fiennes		-> position 0
Michael Gambon		-> position 0
Alan Rickman		-> position 0
Daniel Radcliffe	-> position 0

Alan Howard			-> position 0,136 * supondo que Alan Howard estivesse na listade actors dos dois filmes
Noel Appleby		-> position 136
Sean Astin			-> position 136
Sala Baker			-> position 136

idea:

(function file is the file ptr, x is one json object (the movie) and λ = the lambda function it recieved that recieves a movie and returns a list)
md = {}
for each x=movie in the file:
	for key in λ(x):
		if key in md:
			md[key].append(file.tell())
		else
			md[key] = list(file.tell())