#turn off all variables in sent.html and rerun

from flask import Flask, render_template, request
import sshtunnel
import re
import sentiment_mod as sent
import db_connection_secret as dbconnect
from reddit_api_secret import *
# import featured_words_mod as featuredWords
import pickle

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home_page.html')

@app.route("/about")
def about():
    return "this is the about page"

@app.route('/', methods=['GET', 'POST'])
def my_form_post():
    if request.method == 'POST':
        Subreddit = request.form['Subreddit']
        search_term = request.form['search_term']
        number_of_results = int(request.form['number_of_results'])
        # processed_text = text.upper()
        # processed_text = testing_functions()
        sub_return = search_subreddit(Subreddit, search_term, number_of_results)
        if sub_return is None:
            return render_template('home_page_no_results.html')
        else:
            submission_name_formatted, submission_url_formatted, linked_website_formatted, total_votes, pos, neg, \
            net_sent = sub_return
            # print(processed_text)
            # return processed_text
            return render_template('sent.html', submission_name_formatted=submission_name_formatted,
                                   submission_url_formatted=submission_url_formatted,
                                   linked_website_formatted=linked_website_formatted,
                                   total_votes=total_votes,
                                   pos=pos,
                                   neg=neg,
                                   net_sent=net_sent)
    else:
        return render_template('home_page.html')

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

def sentiment_izer(data_set):
    total_votes = 0
    for sub in data_set:
        total_votes = total_votes + sub[1]
    print('total votes:', total_votes)

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
    print('total positive sentiment:',pos)
    print('total negative sentiment:',neg)
    # print('\n')
    net_sent = pos + neg
    if net_sent > 0:
        print('Positive Sentiment, net sentiments is', net_sent)
    elif net_sent < 0:
        print('Negative Sentiment, net sentiment is', net_sent)
    else:
        print('Your Net Sentiment is zero or something went wrong with the analysis')
    return total_votes, pos, neg, net_sent

def search_subreddit(subreddit_name, search_term, number_of_results):
    linked_website_formatted = ''
    search = reddit.subreddit(subreddit_name)
    iterator = search.search(search_term, limit=number_of_results)

    for submission in iterator:
        submission_name = submission.title
        submission_name_formatted = submission_name
        submission_linked_url = submission.url
        submission_url = submission.permalink
        submission_url_formatted = (str(submission_url))

        if submission_linked_url != submission_url:
            linked_website_formatted += (submission_linked_url)

        testing_file = find_sent(submission)

        total_votes, pos, neg, net_sent = sentiment_izer(testing_file)
        # word_features = featuredWords.feature_words(testing_file, number_of_top_words)

        return submission_name_formatted, submission_url_formatted, linked_website_formatted, total_votes, pos, neg, net_sent


def testing_functions():
    test_return = 'test return'
    return test_return

if __name__== "__main__":
    app.run(debug=True)

