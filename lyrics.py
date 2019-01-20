import requests, re, sqlite3
from bs4 import BeautifulSoup
from genius_info import ACCESS_TOKEN

base_url = "https://api.genius.com"
headers = {"Authorization" : "Bearer " + ACCESS_TOKEN}
search_url = base_url + "/search"
artist_url = base_url + "/artists/"

# take genius artist id and returns out all artist songs in a list
def request_artist_songs(artist_id):
	titles = []
	i = 1

	while True:
		songs_url = artist_url + artist_id + "/songs?per_page=50&page=" + str(i)
		response = requests.get(songs_url, headers=headers)
		json = response.json()

		if len(json["response"]["songs"]) > 0:
			for song in json["response"]["songs"]:
				if song["primary_artist"]["name"].lower() == "flatsound":
					titles.append(song["title"])
			i = i + 1
		else:	break

	return titles


# takes song title and artist name, requests info from the database and returns a response
def request_song_info(song_title, artist_name):
	data = {'q': song_title + ' ' + artist_name}
	response = requests.get(search_url, data=data, headers=headers)

	return response


# take a song url and scrapes the page to find and return the lyrics
def scrape_song_url(url):
	page = requests.get(url)
	html = BeautifulSoup(page.text, 'html.parser')
	lyrics = html.find("div", class_="lyrics").get_text()
	metadata = html.find_all("h3")

	album = "None"
	for labels in metadata:
		search = re.search(r"Album\n.*", labels.get_text())
		if search:
			album = search.group(0)[6:]

	song_data = {"album": album, "lyrics": lyrics}

	return song_data


# takes a song title and artist name, returns the lyrics to that song
def get_lyrics(song_title, artist_name):
	response = request_song_info(song_title, artist_name)
	json = response.json()
	song_info = None

	for hit in json['response']['hits']:
		if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
			song_info = hit
			break

	if song_info:
		song_url = song_info['result']['url']
		return scrape_song_url(song_url)
	else:
		return "No song found"


def make_db():
	path = "flatsound.sqlite3"
	conn = sqlite3.connect(path)
	cur = conn.cursor()

	cur.execute(""" DROP TABLE IF EXISTS albums """)
	cur.execute(""" CREATE TABLE albums (album_name TEXT, album_id INTEGER PRIMARY KEY )""")

	cur.execute(""" DROP TABLE IF EXISTS songs """)
	cur.execute(""" CREATE TABLE songs (song_name TEXT, song_id INTEGER PRIMARY KEY, album_id INTEGER, lyrics TEXT)""")

	conn.commit()

	flatsound_songs = request_artist_songs("359125")
	albumList = []
	songList = []

	for song in flatsound_songs:
		song_data = get_lyrics(song, "Flatsound")

		if song_data["album"] not in albumList:
			albumList.append(song_data["album"])
			cur.execute(""" INSERT INTO albums (album_name, album_id) VALUES (?,?)""", 
				(song_data["album"], len(albumList)) ) 
		album_id = albumList.index(song_data["album"]) + 1

		if song not in songList:
			songList.append(song)
			cur.execute(""" INSERT INTO songs (song_name, song_id, album_id, lyrics) VALUES (?,?,?,?)""", 
				(song, len(songList), album_id, song_data["lyrics"]) )
	conn.commit()

		# print("Title: ", song, "\nAlbum: ", song_data["album"])
		# print("\n\n")


make_db()


