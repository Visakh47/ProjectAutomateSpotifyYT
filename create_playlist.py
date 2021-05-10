import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
import json
import requests
from secrets import spotify_user_id
from secrets import spotify_token

class CreatePlaylist:

    def __init__(self) :
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    #Step 1 : Logging Into Youtube 
    def get_youtube_client(self):
        # Copy and Paste from the YT Data API
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = r"C:\Users\Vk_57\Desktop\Project Spotify\client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
        credentials = flow.run_console()
        #From youtube DATA API
        youtube_client = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
        return youtube_client
    


    #Step 2: Getting the Liked Videos & Creating A Storage(Dictionary) of all the Important Song tags
    def get_liked_videos(self):
        rating = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics", #From Youtube Data API - we get the stats 
            myRating="like"
        )
        response = request.execute() #check this again

    #get important tags from each liked video - and looping through each video
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"])
            
            #Use youtube_dl to collect the song name & artist name 
            video = youtube_dl.YoutubeDL({}).extract_info(
                youtube_url,download=False)
            #using the youtubedl to get the songname and artist from the video url
            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:
                #Saving all the information about the song 
                 self.all_song_info[video_title] = {
                "youtube_url" : youtube_url,
                "song_name" : song_name,
                "artist" : artist,

                #adding the song's uri to spotify
                "spotify_uri": self.get_spotify_uri(song_name,artist) #goes to step 4 and calls it
                }


    #Step 3 : Create new Playlist in Spotify
    def create_playlist(self):
        #Making HTTP requests using python - AIzaSyDpgRZu3oIimTRqwXaS_OuGRVVbB2bFkE0web api

        request_body = json.dumps({
            "name": "Youtube Liked Videos",
            "description": "All Your YT Liked Videos",
             "public": True
        })
        #Specfiying the query or the endpoint 
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
           query,
           data = request_body,
           headers={
               "Content-Type":"application/json",
               "Authorization" : "Bearer{}".format(spotify_token)
            }
        )
        response_json = response.json()

        #returning the playlist id - IP using json
        return response_json["id"] 

        

    #Step 4: Search for the new Song in Spotify
    def get_spotify_uri(self,song_name,artist):
        #searching for the song
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
        song_name,
        artist
        )
        response = requests.get(
            query,
               headers={
               "Content-Type":"application/json",
               "Authorization" : "Bearer{}".format(spotify_token)
            }
        )
        response_json = response.json() #storing json response_json
        songs = response_json["tracks"]["items"] #storing the json in songs having tracks , items -- collect the URL , so playlist knows which specific songs to add

        #Use Only the First Song on The Search List 
        uri = songs[0]["uri"]

        return uri # returns the song


    #Step 5: Add this new song to the playlist
    def add_song_to_playlist(self):
        #ADDING ALL THE LIKED SONGS TO A NEW SPOTIFY PLAYLIST
        #filling up our song dictionary 
        self.get_liked_videos() 

        # collecting all of the uri's from liked videos 
        uris = []
        for song ,info in self.all_song_info.items(): #looping through all songs and appending it to the LIST 
            uris.append(info["spotify_uri"])
        
        #creating playlist in spotify
        playlist_id = self.create_playlist() #calling create_playlist function

        #add all songs into new playlist 
        request_data = json.dumps(uris)
        
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
        #sending all of the requests to the speciifed end point 
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type" : "application/json",
                "Authorization" : "Bearer{}".format(spotify_token)
            }
        )
         
        response_json = response.json()
        return response_json

if __name__ == '__main__': 
    cp = CreatePlaylist() #creating object
    cp.add_song_to_playlist()

