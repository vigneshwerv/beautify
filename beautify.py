import requests
import ast
import subprocess
import glob
import eyed3
import StringIO
from PIL import Image
import os

# Spotify Web API Endpoints
search_endpoint = "https://api.spotify.com/v1/search/"
album_endpoint = "https://api.spotify.com/v1/albums/"

song_list = glob.glob("*.mp3")
for song in song_list:
  command = ["echoprint-codegen", song, "10", "50"]
  output,error = subprocess.Popen(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
  if not error:
    # Parse JSON output of echoprint (as string) to dictionary
    output_json = ast.literal_eval(output)[0]
    r = requests.get(search_endpoint, params={'q': output_json['metadata']['title'], 'type': 'track'})
    album_art = r.json()
    album = requests.get(album_endpoint+""+album_art['tracks']['items'][len(album_art['tracks']['items'])-1]['album']['id'])
    r = requests.get(album_art['tracks']['items'][len(album_art['tracks']['items'])-1]['album']['images'][0]['url'])
    buff = StringIO.StringIO()
    buff.write(r.content)
    buff.seek(0)
    imagedata = buff.getvalue()

    # Open and link mp3 file with eyed3
    eyeTag = eyed3.load(song)
    eyeTag.tag.genre = output_json['metadata']['genre'].decode('unicode-escape')
    eyeTag.tag.artist = output_json['metadata']['artist'].decode('unicode-escape')
    eyeTag.tag.album = album.json()['name'].decode('unicode-escape')
    eyeTag.tag.title = output_json['metadata']['title'].decode('unicode-escape')
    eyeTag.tag.images.set(3,imagedata,"image/jpeg",u'Description')
    eyeTag.tag.save()

    filename, extension = os.path.splitext(song)
    os.rename(song, output_json['metadata']['title'] + extension)
  else:
    print(error)
