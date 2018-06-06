import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sentiment_mod as sent
import db_connection_secret as dbconnect
from twitter_api_secret import *
import re
import time

time_stamp = []

def search_tweets(qurey, number_of_results):
    api = tweepy.API(auth)
    query = qurey
    max_tweets = number_of_results
    searched_tweets = []
    last_id = -1
    while len(searched_tweets) < max_tweets:
        count = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, lang = 'en',count=count, max_id=str(last_id - 1))
            if not new_tweets:
                break
            searched_tweets.extend(new_tweets)
            last_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # depending on TweepError.code, one may want to retry or wait
            # to keep things simple, we will give up on an error
            print(e)
    return searched_tweets

def find_sent_of_tweets(qurey, number_of_results):
    lister_unfiltered = []
    for tweets in search_tweets(qurey, number_of_results):
        tweet_text = tweets.text
        submission_body_lower = tweet_text.lower()
        submission_body_processed = re.sub(r'([^\sa-z])+', '', submission_body_lower)
        # print(submission_body_processed)
        try:
            sentiment_value, confidence = sent.sentiment(submission_body_processed)
            tuper_unfiltered = (tweet_text, sentiment_value, confidence)
            lister_unfiltered.append(tuper_unfiltered)
        except:
            pass

    return lister_unfiltered

def calculate_query_sentiment():
    lister_filtered = []
    tweets_and_timestamps = []
    tweets_and_sent = []
    time_stamp_id = str(time.time())
    time_stamp.append(time_stamp_id)
    tweets_and_timestamps.append(time_stamp[0])
    pos = 0
    neg = 0
    query = "\"pee bottle\""
    sent_of_tweets = find_sent_of_tweets(query, 100)
    for result in sent_of_tweets:
        if result[1] == 'neg':
            # print(result)
            # print(result[1])
            if result[0] == '':
                # print('this was passed '+result[0])
                pass
            if float(result[2]) < 0.85:
                # print('not high enough confidence')
                # print('low confidence')
                pass
            else:
                final_sent = -1.0 * float(result[2])
                # print(final_sent)
                neg = neg + final_sent
                tuper_filtered = (result)
                lister_filtered.append(tuper_filtered)
                tweets_and_timestamps.append(tuper_filtered)
                tweets_and_sent.append(tuper_filtered)
        if result[1] == 'pos':
            # print(result)
            # print(result[1])
            if result[0] == '':
                # print('this was passed '+result[0])
                pass
            else:
                final_sent = float(result[2])
                # print(final_sent)
                pos = pos + final_sent
                # tuper_filtered = (float(time_stamp[0]), result)
                tuper_filtered = (result)
                lister_filtered.append(tuper_filtered)
                tweets_and_timestamps.append(tuper_filtered)
                tweets_and_sent.append(tuper_filtered)
                # tweets_and_timestamps.append(time_stamp[0])
    net_sentiment = pos + neg
    # print(tweets_and_timestamps)
    # for i in tweets_and_timestamps:
    #     print(i)
    return query, net_sentiment, tweets_and_timestamps, tweets_and_sent

dbconnect.truncateLocalTable('biz_sent_main')
print('cleared table: biz_sent_main')

def write_everything_to_main_table():
    # print('beginning write to database')
    query, net_sentiment, main_table_write_return, tweets_and_sent = calculate_query_sentiment()
    execute = ("INSERT INTO "
               "biz_sent_main "
               "(date_time_stamp, post_title, link_to_post, reddit_path_to_post, reddit_post_id, total_votes, net_sentiment) "
               "VALUES (%s,%s,%s,%s,%s,%s,%s)")
    time_stamp_key = time_stamp[0]
    # post_title = full_return[1]
    search_query = query
    link_to_post = ''
    reddit_path_to_post = ''
    # reddit_post_id = full_return[4]
    twitter_post_id = ''
    # total_votes = full_return[5]
    total_likes = 1
    total_pos_votes = ''
    total_neg_votes = ''
    net_sentiment_twitter = net_sentiment
    data = time_stamp_key,search_query,link_to_post,reddit_path_to_post,twitter_post_id,total_likes,net_sentiment
    dbconnect.dbLocalInsert(execute, data)

write_everything_to_main_table()

dbconnect.truncateLocalTable('biz_sent_twitter')
print('cleared table: biz_sent_reddit')

def write_everything_to_post_sent_table():
    query, net_sentiment, main_table_write_return, tweets_and_sent = calculate_query_sentiment()
    time_stamp_key = time_stamp[0]
    query_from_search = query
    # print(tweets_and_sent)
    # print('beginning write to database')
    execute = ("INSERT INTO "
               "biz_sent_twitter"
               "(time_stamp, query_from_search, twitter_text, twitter_confidence, twitter_sentiment)"
               "VALUES (%s,%s,%s,%s,%s)")
    for i in range(len(tweets_and_sent)):
        # time_stamp_key = time_stamp[0]
        tweet_sent_confidence = tweets_and_sent[i]
        twitter_text = tweet_sent_confidence[0]
        twitter_senitment = tweet_sent_confidence[1]
        twitter_confidence = tweet_sent_confidence[2]
        data = time_stamp_key, query_from_search, twitter_text, twitter_confidence, twitter_senitment
        dbconnect.dbLocalInsert(execute, data)

write_everything_to_post_sent_table()

# x = calculate_query_sentiment()

#streaming tweets class - currently not using streaming
# class listener(StreamListener):
#
#     def on_data(self, data):
#
#         all_data = json.loads(data)
#
#         tweet = all_data["text"]
#         sentiment_value, confidence = sent.sentiment(tweet)
#         print(tweet, sentiment_value, confidence)
#
#         if confidence*100 >= 80:
#             output = open("twitter-out.txt","a")
#             output.write(sentiment_value)
#             output.write('\n')
#             output.close()
#
#         return True
#
#     def on_error(self, status):
#         print(status)