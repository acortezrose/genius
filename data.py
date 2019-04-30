# alexandra cortez
# use db info to analyze song lyrics

import sqlite3, re, string
import matplotlib.pyplot as plt

path = "flatsound.sqlite3"
conn = sqlite3.connect(path)
cur = conn.cursor()
albums = {}

def analyze():
	print("analyzing lyrics...")
	rows = cur.execute(""" SELECT * FROM albums """)
	for row in rows:
		albums[row[1]] = {"name" : row[0], "tracklist": [], "data" : {} }

	rows = cur.execute(""" SELECT * FROM songs """)
	for row in rows:
		parseLyrics(row)

	for key, value in albums.items():
		fig = plt.figure(figsize=(10,4), dpi=100)

		name = value["name"]
		data = sorted(value["data"].items(), key=lambda kv: kv[1], reverse=True)
		keys, values = zip(*data)

		topkeys = keys[0:15]
		topvalues = values[0:15]

		ax = plt.subplot(1,1,1)
		ax.bar(topkeys, topvalues, color="gray")
		ax.set_xlabel("word")
		ax.set_ylabel("num")
		ax.set_title(name)

		album = name.translate(str.maketrans('', '', string.punctuation))
		fig.savefig("figs/"+album+".png")

def report():
	print("---------- report ----------")
	alltime = {}

	for key,value in albums.items():
		for word, count in value["data"].items():
			alltime[word] = alltime.get(word, 0) + count

	alltimesorted = sorted(alltime.items(), key=lambda kv: kv[1], reverse=True)

	print(alltimesorted)

	vocabsize = len(alltimesorted)

	print("VOCAB SIZE = ", vocabsize)


def parseLyrics(row):
	song_name = row[0]
	song_id = row[1]
	album_id = row[2]
	lyrics = row[3]

	albums[album_id]["tracklist"].append(song_name)

	words = lyrics.split()
	for word in words:
		word = word.lower()
		word = word.translate(str.maketrans('', '', string.punctuation))
		word = word.replace("'", "")
		word = word.replace("’", "")
		

		albums[album_id]["data"][word] = albums[album_id]["data"].get(word, 0) + 1



analyze()
report()
