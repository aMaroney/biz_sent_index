import praw
import pymysql
import sshtunnel
import time
import requests
import re
# import sentiment_mod as sent
import db_connection_secret as dbconnect
from reddit_api_secret import *


sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

# hot_python = subreddit.hot(limit = 4)

def reddit_API_call(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    submission = reddit.submission(url='https://www.reddit.com/r/orlando/comments/88j45i/did_someone_lose_their_dog_found_in_wadeview_park/')
    # submission = reddit.submission(url='https://www.reddit.com/r/orlando/comments/8clikx/i_went_to_taco_maker_mexican_grill_a_new/')
    return submission


submission = reddit_API_call('orlando')

#need to change so that everything from reddits api posts in the table
def insert_text_into_table():
    execute =("INSERT INTO biz_sent_text (reddit_text) VALUES (%s)")
    submission_body = submission.selftext
    submission_body_lower = submission_body.lower()
    submission_body_processed = re.sub(r'([^\sa-z])+', '', submission_body_lower)
    data = submission_body_processed
    dbconnect.dbRemoteInsert(execute, data)
    for comment in submission.comments.list():
        comment_score = comment.score
        comment_body = comment.body
        comment_body_lower = comment_body.lower()
        comment_body_processed = re.sub(r'([^\sa-z])+', '', comment_body_lower)
        data = comment_body_lower
        dbconnect.dbRemoteInsert(execute, data)

# insert_text_into_table()

data_from_db = []

#need to make this pull all the reddit info from table and write to a tuple
def pull_text_from_table():
    execute = 'SELECT reddit_text FROM biz_sent_text'
    table_text = dbconnect.dbRemotePull(execute)
    return table_text
    # for i in range(len(table_text)):
        # data_from_db.append(table_text[i])

# dictionary = {}
dictionary = {'': 'neg', 'you are a good man/woman!': 'pos', 'did you check at a vets to see if the dog has a chip?': 'neg', 'cutie': 'neg', 'update: took to pound and he is microchipped :) he\x92ll be reunited with his owner ': 'neg', 'i hope you find the owner :(': 'neg', 'aw, good! he\x92s a sweetie!': 'pos'}

#need to add sent to end of tuble for each text
def find_submission_sent():
    table_text = pull_text_from_table()
    # print(table_text)
    for tups in range(len(table_text)):
        for text in table_text[tups]:
            sentiment_value, confidence = sent.sentiment(text)
            dictionary[text] = sentiment_value
    return True

# find_submission_sent()

#need to write final tuple to new table
def write_everything_to_table():
    # execute = ("INSERT INTO biz_sent_main (reddit_text, sentiment, confidence, reddit_score) VALUES (%s,%s,%s,%s)")
    execute = ("INSERT INTO biz_sent_main (reddit_text, sentiment, reddit_score) VALUES (%s,%s,%s)")
    # for i in range(len(dictionary))
    for key, value in dictionary.items():
        submission_body_processed = key
        sentiment = value
        reddit_score = submission.comment.score
        data = submission_body_processed, sentiment, reddit_score
        dbconnect.dbRemoteInsert(execute, data)

    # confidence =
    # reddit_score =

    # data = submission_body_processed, sentiment, confidence, reddit_score
    # for comment in submission.comments.list():
    #     comment_score = comment.score
    #     comment_body = comment.body
    #     comment_body_lower = comment_body.lower()
    #     comment_body_processed = re.sub(r'([^\sa-z])+', '', comment_body_lower)
    #     data = comment_body_lower
    #     dbconnect.dbRemoteInsert(execute, data)

write_everything_to_table()

def write_post_to_keys():
    submission_body = submission.selftext
    submission_body_lower = submission_body.lower()
    no_special_char = re.sub(r'([^\sa-z])+', '', submission_body_lower)
    dictionary[no_special_char] = ''

    for comment in submission.comments.list():
        comment_score = comment.score
        comment_body = comment.body
        comment_body_lower = comment_body.lower()
        no_special_char = re.sub(r'([^\sa-z])+', '', comment_body_lower)
        dictionary[no_special_char] = ''

# def find_submission_sent():
#     for key in dictionary.keys():
#         try:
#             submission = key
#             sentiment_value, confidence = sent.sentiment(submission)
#             for key in dictionary.keys():
#                 if key == submission:
#                     dictionary[key] = sentiment_value
#             # print(submission, sentiment_value, confidence)
#         except Exception as e:
#             print(e)
#     return True