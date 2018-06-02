import db_connection_secret as dbconnect
import matplotlib.pyplot as plt

pos_and_neg_totals = []

execute = ('SELECT post_title,reddit_post_id,total_votes,net_sentiment FROM biz_sent_main')
result_from_main = dbconnect.dbLocalPullGeneral(execute)


def graph_post(post_id):
    data= post_id
    execute = ("SELECT time_stamp, reddit_text, reddit_score, reddit_post_id  FROM biz_sent_reddit")
    result = dbconnect.dbLocalPullGeneral(execute)
    pos = 0.0
    neg = 0.0
    for comment in result:
        if comment[3] == data:
            sentiment = float(comment[2])
            if sentiment > 0.0:
                pos += sentiment
            if sentiment < 0.0:
                neg += abs(sentiment)
            else:
                pass
        else:
            pass
    pos_and_neg_totals.append(pos)
    pos_and_neg_totals.append(neg)


    # # Data to plot
    labels = 'Positive', 'Negative'
    colors = ['lightskyblue', 'lightcoral']
    explode = (0.1, 0)  # explode 1st slice

    # Plot
    plt.title('Positive and Negative Sentiment')
    plt.pie(pos_and_neg_totals, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)

    plt.axis('equal')
    plt.show()

graph_post('88inz6')