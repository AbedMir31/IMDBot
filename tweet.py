import tweepy
from os import environ
from imdb import IMDb, IMDbError

CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']

# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Attempt to authenticate
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

try:
    imdb_obj = IMDb()
    print("IMDb link OK")
except:
    print("Error during access to IMDb server")


# Create stream object to wait for mentions
class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print("INCOMING TWEET by @%s:\n%s" % (status.user.name, status.text))
        replyID = status.id
        if "Search" or "search" or "look up" or "Look up" or "lookup" in status.text:
            query = status.text.replace('@givemearating ', '')
            query = query.replace('search', '')
            try:
                results = imdb_obj.search_movie(query)
                movie = imdb_obj.get_movie(results[0].getID())
                imdb_obj.update(movie, ['main', 'vote details'])
                print("%s, %s" % (movie.get('title'), movie.get('year')))
                print("Rating: %s" % movie.get('rating'))

                str_tweet = "%s, %s" % (movie.get('title'), movie.get('year')) + "\nRating: %s" % movie.get('rating')
                api.update_status(status=str_tweet, in_reply_to_status_id=replyID, auto_populate_reply_metadata=True)
            except IMDbError as e:
                print(e)

    def on_error(self, status):
        print("Error Detected")


myListener = MyStreamListener(api)
myStream = tweepy.Stream(auth=api.auth, listener=myListener)

print("Stream created OK")
myStream.filter(track=["@givemearating"], languages=["en"])

# Integrate imdb next
