import sshtunnel
import re
import sentiment_mod as sent
import db_connection_secret as dbconnect
from reddit_api_secret import *
import featured_words_mod as featuredWords
import pickle
import pprint

full_return = []

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

def reddit_post_fetch(post_url):
    submission = reddit.submission(url=post_url)
    return submission

def find_sent(submissionID):
    submission = submissionID
    tuper = ()
    lister = []
    submission_body = submission.selftext
    submission_body_lower = submission_body.lower()
    submission_body_processed = re.sub(r'([^\sa-z])+', '', submission_body_lower)
    reddit_score = submission.score
    try:
        sentiment_value, confidence = sent.sentiment(submission_body_processed)
        tuper = (submission_body, reddit_score, sentiment_value, confidence)
        lister.append(tuper)
    except:
        pass

    for comment in submission.comments.list():
        try:
            comment_score = comment.score
            comment_body = comment.body
            comment_body_lower = comment_body.lower()
            comment_body_processed = re.sub(r'([^\sa-z])+', '', comment_body_lower)
            reddit_score = comment_score
            try:
                sentiment_value, confidence = sent.sentiment(comment_body_processed)
                tuper = (comment_body, reddit_score, sentiment_value, confidence)
                lister.append(tuper)
            except:
                pass
        except:
            pass

    return lister

pickle_in = open('testing.pickle', 'rb')
testing_file = pickle.load(pickle_in)
pickle_in.close()

# testing_file = find_sent(submission)

pickle_out = open('testing.pickle', 'wb')
pickle.dump(testing_file, pickle_out)
pickle_out.close()

def sentiment_izer(data_set):
    total_votes = 0
    for sub in data_set:
        total_votes = total_votes + sub[1]
    total_votes_return  = 'total votes:', total_votes
    print(total_votes_return)

    pos = 0
    neg = 0
    for i in range(len(data_set)):
        if data_set[i][2] == 'neg':
            if data_set[i][0] == '':
                # print('blank text for submission or comment')
                pass
            if float(data_set[i][3]) < 0.85:
                # print('low confidence')
                pass
            else:
                # print(data_set[i])
                scale_with_conf = data_set[i][3] * 1
                # print(scale_with_conf)
                vote_scaler = 1 + (data_set[i][1] / total_votes)
                # print(vote_scaler)
                scale_with_vote = float(scale_with_conf) * vote_scaler
                # print(scale_with_vote)
                final_sent = -1.0 * float(scale_with_vote)
                # print(final_sent)
                neg = neg + final_sent
        if data_set[i][2] == 'pos':
            if data_set[i][0] == '':
                # print('blank text for submission or comment')
                pass
            else:
                # print(data_set[i])
                scale_with_conf = data_set[i][3] * 1
                # print(scale_with_conf)
                vote_scaler = 1 + (data_set[i][1] / total_votes)
                # print(vote_scaler)
                scale_with_vote = float(scale_with_conf) * vote_scaler
                # print(scale_with_vote)
                final_sent = 1.0 * float(scale_with_vote)
                # print(final_sent)
                pos = pos + final_sent
    # print('\n')
    total_pos = 'total positive sentiment:',pos
    total_neg = 'total negative sentiment:',neg
    print(total_pos)
    print(total_neg)
    # print('\n')
    net_sent = pos + neg
    net_sent_final = ''
    if net_sent > 0:
        net_sent_return = 'Positive Sentiment, net sentiments is', net_sent
        net_sent_final += str(net_sent_return)
        print(net_sent_return)
    elif net_sent < 0:
        net_sent_return = 'Negative Sentiment, net sentiment is', net_sent
        net_sent_final += str(net_sent_return)
        print(net_sent_return)
    else:
        print('Your Net Sentiment is zero or something went wrong with the analysis')
    full_return.append(total_votes_return)
    full_return.append(total_pos)
    full_return.append(total_neg)
    full_return.append(net_sent_final)

def search_subreddit(subreddit_name, search_term, number_of_results, number_of_top_words):
    search = reddit.subreddit(subreddit_name)
    iterator = search.search(search_term, limit=number_of_results)
    for submission in iterator:
        submission_name = submission.title
        print('Submission Title:',submission_name)

        submission_linked_url = submission.url
        submission_url = submission.permalink
        print('Submission url:','https://www.reddit.com'+str(submission_url))
        if submission_linked_url != submission_url:
            print('Linked website from submission:',submission_linked_url)

        testing_file = find_sent(submission)

        sentiment_izer(testing_file)
        full_return.append(submission_name)
        full_return.append(submission_linked_url)
        full_return.append(submission_url)

sub_return = search_subreddit('orlando', 'sprint', 10, 1)

#testing for web app interface
# print(full_return)

#this check isn't really needed for the command line version
# if sub_return is None:
#     print('No results were found for your search term and subreddit combination')
# else:
#     pass


# dbconnect.truncateLocalTable('biz_sent_reddit')
# print('cleared table: biz_sent_reddit')
#
# dbconnect.truncateLocalTable('biz_sent_main')
# print('cleared table: biz_sent_main')

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
        # dbconnect.dbRemoteInsert(execute, data)
        dbconnect.dbLocalInsert(execute, data)

# write_everything_to_main_table()
# print('inserted everything into the main table')
