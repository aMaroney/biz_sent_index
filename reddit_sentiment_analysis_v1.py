import re
import sentiment_mod as sent
import db_connection_secret as dbconnect
from reddit_api_secret import *
import featured_words_mod as featuredWords
import time

full_return = []
post_return = []
time_stamp = []

# dbconnect.truncateLocalTable('biz_sent_main')
# print('cleared table: biz_sent_main')

def write_everything_to_main_table():
    # print('beginning write to database')
    execute = ("INSERT INTO "
               "biz_sent_main "
               "(date_time_stamp, post_title, link_to_post, reddit_path_to_post, reddit_post_id, total_votes, net_sentiment) "
               "VALUES (%s,%s,%s,%s,%s,%s,%s)")
    time_stamp = full_return[0]
    post_title = full_return[1]
    link_to_post = full_return[2]
    reddit_path_to_post = full_return[3]
    reddit_post_id = full_return[4]
    total_votes = full_return[5]
    total_pos_votes = full_return[6]
    total_neg_votes = full_return[7]
    net_sentiment = full_return[8]
    data = time_stamp,post_title,link_to_post,reddit_path_to_post,reddit_post_id,total_votes,net_sentiment
    dbconnect.dbLocalInsert(execute, data)

# dbconnect.truncateLocalTable('biz_sent_reddit')
# print('cleared table: biz_sent_reddit')

def write_everything_to_post_sent_table():
    # print('beginning write to database')
    execute = ("INSERT INTO "
               "biz_sent_reddit"
               "(time_stamp, reddit_text, reddit_score, reddit_post_id)"
               "VALUES (%s,%s,%s,%s)")
    for i in range(len(post_return)):
        time_stamp = post_return[i][0]
        reddit_text = post_return[i][2]
        reddit_score = post_return[i][1]
        reddit_post_id = full_return[4]
        data = time_stamp, reddit_text,reddit_score, reddit_post_id
        dbconnect.dbLocalInsert(execute, data)

def reddit_post_fetch(post_url):
    submission = reddit.submission(url=post_url)
    return submission

def find_sent(submissionID):
    submission = submissionID
    lister_unfiltered = []
    submission_body = submission.selftext
    submission_body_lower = submission_body.lower()
    submission_body_processed = re.sub(r'([^\sa-z])+', '', submission_body_lower)
    reddit_score = submission.score
    try:
        sentiment_value, confidence = sent.sentiment(submission_body_processed)
        tuper_unfiltered = (submission_body, reddit_score, sentiment_value, confidence)
        lister_unfiltered.append(tuper_unfiltered)
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
                tuper_unfiltered = (comment_body, reddit_score, sentiment_value, confidence)
                lister_unfiltered.append(tuper_unfiltered)
            except:
                pass
        except:
            pass
    # lister_unfiltered looks like ('Switching to Sprint is a bad idea', 31, 'neg', 1.0)
    return lister_unfiltered

def sentiment_izer(data_set):
    tuper_filtered = ()
    lister_filtered = []
    total_votes = 0
    for sub in data_set:
        total_votes = total_votes + sub[1]
    total_votes_return  = 'total votes: '+ str(total_votes)
    print(total_votes_return)
    pos = 0
    neg = 0
    for i in range(len(data_set)):
        reddit_comment = data_set[i][0]
        reddit_comment_votes = data_set[i][1]
        reddit_comment_sentiment = data_set[i][2]
        reddit_comment_sentiment_confidence = data_set[i][3]
        if reddit_comment_sentiment == 'neg':
            if reddit_comment == '':
                pass
            if float(reddit_comment_sentiment_confidence) < 0.85:
                # print('low confidence')
                pass
            else:
                vote_scaler = 1 + (reddit_comment_votes / total_votes)
                scale_with_vote = float(reddit_comment_sentiment_confidence) * vote_scaler
                final_sent = -1.0 * float(scale_with_vote)
                neg = neg + final_sent
                tuper_filtered = (float(time_stamp[0]), final_sent, reddit_comment)
                lister_filtered.append(tuper_filtered)
                post_return.append(tuper_filtered)
        if reddit_comment_sentiment == 'pos':
            if reddit_comment == '':
                pass
            else:
                vote_scaler = 1 + (reddit_comment_votes / total_votes)
                scale_with_vote = float(reddit_comment_sentiment_confidence) * vote_scaler
                final_sent = 1.0 * float(scale_with_vote)
                pos = pos + final_sent
                tuper_filtered = (float(time_stamp[0]), final_sent, reddit_comment)
                lister_filtered.append(tuper_filtered)
                post_return.append(tuper_filtered)
    # print('\n')
    total_pos = 'total positive sentiment: ' + str(pos)
    total_neg = 'total negative sentiment: ' + str(neg)
    print(total_pos)
    print(total_neg)
    # print('\n')
    net_sent = pos + neg
    net_sent_final = ''
    if net_sent > 0:
        net_sent_return = 'Positive Sentiment, net sentiments is ' + str(net_sent)
        net_sent_final += str(net_sent_return)
        print(net_sent_return)
        print('\n')
    elif net_sent < 0:
        net_sent_return = 'Negative Sentiment, net sentiment is ' + str(net_sent)
        net_sent_final += str(net_sent_return)
        print(net_sent_return)
        print('\n')
    else:
        print('Your Net Sentiment is zero or something went wrong with the analysis')
    full_return.append(total_votes)
    full_return.append(pos)
    full_return.append(neg)
    full_return.append(net_sent)

def search_subreddit(subreddit_name, search_term, number_of_results, number_of_top_words):
    search = reddit.subreddit(subreddit_name)
    iterator = search.search(search_term, limit=number_of_results)
    runs = 0
    for submission in iterator:
        submission_id = submission.id
        time_stamp_id = str(time.time())
        time_stamp.append(time_stamp_id)
        submission_name = submission.title
        print('Submission Title:',submission_name)

        submission_linked_url = submission.url
        submission_url = submission.permalink
        print('Submission url:','https://www.reddit.com'+str(submission_url))
        if submission_linked_url != submission_url:
            pass
        full_return.append(time_stamp_id)
        full_return.append(submission_name)
        full_return.append(submission_linked_url)
        full_return.append(submission_url)
        full_return.append(submission_id)
        testing_file = find_sent(submission)
        sentiment_izer(testing_file)
        runs += 1
        write_everything_to_main_table()
        # print('inserted '+str(runs)+'/'+str(number_of_results)+' results to your search into the db')
        write_everything_to_post_sent_table()
        del full_return[:]
        del post_return[:]

subreddit = input('what subreddit would you like to search? ')
search_term = input('what is the search term you would like to use? ')
number_of_results = input('how many results would you like? ')
print('okay, fetching resluts\n')
sub_return = search_subreddit(subreddit, search_term, int(number_of_results), 1)