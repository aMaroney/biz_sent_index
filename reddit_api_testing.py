import praw
import pymysql
import sshtunnel
import time
import requests
import re
import sentiment_mod as sent
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

def insert_text_into_table():
    execute =("INSERT INTO biz_sent (reddit_text) VALUES (%s)")
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

insert_text_into_table()

data_from_db = []

def pull_text_from_table():
    execute = 'SELECT reddit_text FROM biz_sent'
    dbconnect.dbRemotePull(execute)

dictionary = {}

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

# write_post_to_keys()

def find_submission_sent():
    for key in dictionary.keys():
        try:
            submission = key
            sentiment_value, confidence = sent.sentiment(submission)
            for key in dictionary.keys():
                if key == submission:
                    dictionary[key] = sentiment_value
            # print(submission, sentiment_value, confidence)
        except Exception as e:
            print(e)
    return True

# find_submission_sent()

def dbConnectionLocal(host, user, password, database):
    try:
        connection = pymysql.connect(host=host,user=user,password=password,database=database,use_unicode=True, charset="utf8")
        return connection
    except Exception as e:
                print(e)