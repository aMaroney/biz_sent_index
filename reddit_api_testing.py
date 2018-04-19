import praw
import pymysql
import sshtunnel
import time
import requests
import re
import sentiment_mod as sent
from reddit_api_secret import *


# hot_python = subreddit.hot(limit = 4)

def reddit_API_call(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    # submission = reddit.submission(url='https://www.reddit.com/r/orlando/comments/88j45i/did_someone_lose_their_dog_found_in_wadeview_park/')
    submission = reddit.submission(url='https://www.reddit.com/r/orlando/comments/8clikx/i_went_to_taco_maker_mexican_grill_a_new/')
    return submission


submission = reddit_API_call('orlando')

submission_body_filtered = []
submission_score = []
submission_sent = []

def get_submission():
    submission_body = submission.selftext
    submission_body_lower = submission_body.lower()
    no_special_char = re.sub(r'([^\sa-z])+', '', submission_body_lower)
    submission_body_filtered.append(no_special_char)
    submission_score.append(submission.score)
    return True

get_submission()

comment_body_list_filtered = []
comment_score_list = []
comment_sent = []

def get_comments():
    for comment in submission.comments.list():
        comment_score = comment.score
        comment_body = comment.body
        comment_body_lower = comment_body.lower()
        no_special_char = re.sub(r'([^\sa-z])+', '', comment_body_lower)
        comment_body_list_filtered.append(no_special_char)
        comment_score_list.append(comment.score)

get_comments()

def find_submission_sent():
    for submission_iter in range(len(submission_body_filtered)):
        try:
            submission = submission_body_filtered[submission_iter]
            sentiment_value, confidence = sent.sentiment(submission)
            submission_sent.append(sentiment_value)
            # print(submission, sentiment_value, confidence)
        except Exception as e:
            submission_sent.append()
    return True

find_submission_sent()

def find_comment_sent():
    for comment_iter in range(len(comment_body_list_filtered)):
        try:
            comment = comment_body_list_filtered[comment_iter]
            sentiment_value, confidence = sent.sentiment(comment)
            comment_sent.append(sentiment_value)
            # print(comment, sentiment_value, confidence)
        except Exception as e:
            if Exception == 'no unique mode; found 2 equally common values':
                pass
            else:
                print(type(e))
    return True

find_comment_sent()

# for submission in hot_python:
#     print(dir(submission))
# subreddit_title = (subreddit.title)
# submission_title = (submission.title)
# submission_id = (submission.id)
# submission_score = (submission.score)
# submission_url = (submission.url)
# submission_utc_created = (submission.created_utc)
# submission_text = submission.selftext
# print('submission_title: ',submission_title)
# print('submission_score: ', submission_score)
# print(subreddit_title,'\n',submission_title,'\n',submission_id,'\n',submission_score,'\n',submission_url,'\n',submission_utc_created)
# for comment in submission.comments.list():
#     # print(20 * '-')
#     parent_id = str(comment.parent())
#     comment_id =  comment.id
#     comment_score = comment.score
#     comment_body = comment.body
#     # print(dir(comment))
#     comment_time = comment.created_utc
#     comment_link = comment.permalink
    # print(subreddit_title, '\n', submission_title, '\n', submission_id, '\n', submission_score, '\n', submission_url,
    #       '\n', submission_utc_created)
    # print('comment_score: '+str(comment_score),'\n','comment_body: '+comment_body,'\n')
    # print('parent_id: '+parent_id,'\n',
    #                    'comment_id: '+comment_id,'\n',
    #                                  'comment_score: '+str(comment_score),'\n',
    #                                                   'comment_body: '+comment_body,'\n',
    #                                                                   'comment_time: '+str(comment_time),'\n',
    #                                                                                   'comment_link: '+comment_link)
    # submission = comment_body
    # sentiment_value, confidence = sent.sentiment(submission)
    # print(submission, '\n',sentiment_value, '\n',confidence)
    # print('-----------------------------------------------------')

    # if confidence * 100 >= 80:
        # output = open("reddit-out.txt","a")
        # output.write(sentiment_value)
        # output.write('\n')
        # output.close()
        # print(sentiment_value)


# def on_data(data):


# submission = submission_title
# sentiment_value, confidence = sent.sentiment(submission)
# print(submission, sentiment_value, confidence)
# submission = submission_text
# sentiment_value, confidence = sent.sentiment(submission)
# print('submission_text', sentiment_value, confidence)

# if confidence*100 >= 80:
    # output = open("reddit-out.txt","a")
    # output.write(sentiment_value)
    # output.write('\n')
    # output.close()
    # print(sentiment_value)
# return True

def dbConnectionLocal(host, user, password, database):
    try:
        connection = pymysql.connect(host=host,user=user,password=password,database=database,use_unicode=True, charset="utf8")
        return connection
    except Exception as e:
                print(e)

def insertIntoTable():
    connection = dbConnectionLocal('localhost', 'root', 'xxxx!', 'biz_index1')
    cursor = connection.cursor()
    subreddit_title = (subreddit.title)
    submission_title = (submission.title)
    submission_id = (submission.id)
    submission_score = (submission.score)
    submission_url = (submission.url)
    submission_utc_created = (submission.created_utc)
    for comment in submission.comments.list():
        # print(20 * '-')
        parent_id = str(comment.parent())
        comment_id = comment.id
        comment_score = comment.score
        comment_body = comment.body
        # print(dir(comment))
        comment_time = comment.created_utc
        comment_link = comment.permalink
        unix_time = time.time()
        cursor.execute(
            "INSERT INTO biz_table1"
            "("
            "subreddit_title, "
            "submission_title, "
            "submission_id, "
            "submission_score, "
            "submission_url, "
            "submission_utc_created,"
            " comment_parent_id, "
            "comment_comment_id, "
            "comment_score, "
            "comment_body, "
            "comment_time, "
            "comment_link"
            ")"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (subreddit_title,
             submission_title,
             submission_id,
             submission_score,
             submission_url,
             submission_utc_created,
             parent_id,
             comment_id,
             comment_score,
             comment_body,
             comment_time,
             comment_link
             ))
    connection.commit()
    connection.close()

# Python code to remove duplicate elements
def Remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list

def extractFromTable():
    submission_id_list = []
    connection = dbConnectionLocal('localhost', 'root', 'xxxx!', 'biz_index1')
    cursor = connection.cursor()
    cursor.execute('SELECT submission_title, comment_body FROM biz_table1')
    submission_title = cursor.fetchall()
    for row in submission_title:
        print(row)
    connection.commit()
    connection.close()

# insertIntoTable()
# extractFromTable()