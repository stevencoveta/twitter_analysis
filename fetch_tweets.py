import tweepy
import pandas as pd 

api_key = "GosyQglUdrbp2zIuTXYEuYLkU"
api_secrets = "SEwKdTCQ6S81TbIhTtWZuhOmHen58nLZJshj8dSOrTWrulKbbr"
access_token = "1589592172277506048-riv1iWYnHrnSWXeA5Xk5gfplmabyKS"
access_secret = "b5rB61Eifd7oexWMXkXcEOhG47jqXCp14OcF59kviCrA0"
 
auth = tweepy.OAuthHandler(api_key,api_secrets)
auth.set_access_token(access_token,access_secret)
 
api = tweepy.API(auth, wait_on_rate_limit=True)
 
try:
    api.verify_credentials()
    print('Successful Authentication')
except:
    print('Failed authentication')


def get_last_tweet(userID):
    tweets = api.user_timeline(screen_name=userID, 
                           # 200 is the maximum allowed count
                           count=100,
                           include_rts = False,
                           exclude_replies = True,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended')
                           #max_id = last_id[-1])

    tweets_date = []
    tweets_text = []
    ids = []
    try: 
        for info in tweets:
            tweets_date.append(info.created_at)
            tweets_text.append(info.full_text)
            ids.append(info.id)

        last_id = ids
        return max(last_id)
    except Exception as e: 
        print(e)


def get_tweets(userID):
    max_tweet_id = get_last_tweet(userID)
    print(f"fetching tweets of {userID}")
    try:
        for _ in range(15):
            tweets = api.user_timeline(screen_name=userID, 
                           count=200,
                           include_rts = False,
                           exclude_replies = False,
                           tweet_mode = 'extended', 
                           max_id = max_tweet_id)

            tweets_date = []
            tweets_text = []
            ids_tweet = []
            for info in tweets:
                tweets_date.append(info.created_at)
                tweets_text.append(info.full_text)
                ids_tweet.append(info.id)
                
            print("finished collecting tweets")
            tweets_complete = {"date":tweets_date, 
                    "tweet":tweets_text, 
                    "ids":ids_tweet}
            return pd.DataFrame(tweets_complete)  
        
    except Exception as e:
        print(e) 
        
