import sshtunnel
import re
import sentiment_mod as sent
import db_connection_secret as dbconnect
from reddit_api_secret import *
import pickle


sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

# hot_python = subreddit.hot(limit = 4)

dbconnect.truncateRemoteTable('biz_sent_reddit')
print('cleared table: biz_sent_reddit')
dbconnect.truncateRemoteTable('biz_sent_main')
print('cleared table: biz_sent_main')

def reddit_API_call(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    # submission = reddit.submission(url='https://www.reddit.com/r/orlando/comments/88j45i/did_someone_lose_their_dog_found_in_wadeview_park/')
    # submission = reddit.submission(url='https://www.reddit.com/r/orlando/comments/8clikx/i_went_to_taco_maker_mexican_grill_a_new/')
    # submission = reddit.submission(
    #     url='https://www.reddit.com/r/orlando/comments/88inz6/tell_me_switching_to_sprint_is_a_bad_idea/')
    submission = reddit.submission(
        url='https://www.reddit.com/r/orlando/comments/8d8wqi/voodoo_donut_dont_believe_the_hype/')
    return submission


submission = reddit_API_call('orlando')

def insert_text_and_score_into_table():
    execute =("INSERT INTO biz_sent_reddit (reddit_text, reddit_score) VALUES (%s, %s)")
    submission_body = submission.selftext
    submission_body_lower = submission_body.lower()
    submission_body_processed = re.sub(r'([^\sa-z])+', '', submission_body_lower)
    reddit_score = submission.score
    data = submission_body_processed, reddit_score
    dbconnect.dbRemoteInsert(execute, data)
    for comment in submission.comments.list():
        comment_score = comment.score
        comment_body = comment.body
        comment_body_lower = comment_body.lower()
        comment_body_processed = re.sub(r'([^\sa-z])+', '', comment_body_lower)
        reddit_score = comment_score = comment.score
        data = comment_body_lower, reddit_score
        dbconnect.dbRemoteInsert(execute, data)

insert_text_and_score_into_table()
print('inserted into reddit table')

def pull_text_and_score_from_table():
    execute = 'SELECT reddit_text, reddit_score FROM biz_sent_reddit'
    table_text = dbconnect.dbRemotePull(execute)
    return table_text

#dictionary[text] = sentiment_value


def find_sent():
    tuper = ()
    table_text = pull_text_and_score_from_table()
    for i in range(len(table_text)):
        for text in table_text:
            try:
                sentiment_value, confidence = sent.sentiment(text[i])
                text = text + (sentiment_value, confidence)
                tuper = tuper + (text,)
            except Exception as e:
                pass
    return tuper


sent_result = find_sent()
print('found the sentiment')

pickle_out = open('testing.pickle', 'wb')
pickle.dump(sent_result, pickle_out)
pickle_out.close()
print('pickled test')

pickle_in = open('testing.pickle', 'rb')
testing_file = pickle.load(pickle_in)
pickle_in.close()

def write_everything_to_main_table():
    # execute = ("INSERT INTO biz_sent_main (reddit_text, sentiment, confidence, reddit_score) VALUES (%s,%s,%s,%s)")
    execute = ("INSERT INTO biz_sent_main (reddit_text, sentiment, confidence, reddit_score) VALUES (%s,%s,%s,%s)")
    # for i in range(len(dictionary))
    for tup in range(len(testing_file)):
        text = testing_file[tup][0]
        reddit_score = testing_file[tup][1]
        sent = testing_file[tup][2]
        confidence = testing_file[tup][3]
        data = text, sent, confidence, reddit_score
        dbconnect.dbRemoteInsert(execute, data)

write_everything_to_main_table()
print('inserted everything into the main table')