import db_connection_secret as dbconnect

def pull_text_and_score_from_table():
    execute = 'SELECT * FROM biz_sent_main'
    table_text = dbconnect.dbRemotePull(execute)
    return table_text

table = pull_text_and_score_from_table()
print(table)
total_votes = 0
for sub in table:
    total_votes = total_votes + sub[3]
vote_scaler = 1 + (table[1][3]/total_votes)

pos = 0
neg = 0

for review in table:
    for i in range(len(table)):
        # print(table[i])
        if table[i][1] == 'neg':
            if table[i][0] == '':
                pass
            if float(table[i][2]) < 0.85:
                pass
            else:
                scale_with_conf = table[i][2] * 1
                # print(scale_with_conf)
                vote_scaler = 1 + (table[i][3] / total_votes)
                # print(vote_scaler)
                scale_with_vote = float(scale_with_conf) * vote_scaler
                # print(scale_with_vote)
                final_sent = -1.0 * float(scale_with_vote)
                # print(final_sent)
                neg = neg + final_sent
        if table[i][1] == 'pos':
            if table[i][0] == '':
                pass
            else:
                scale_with_conf = table[i][2] * 1
                # print(scale_with_conf)
                vote_scaler = 1 + (table[i][3] / total_votes)
                # print(vote_scaler)
                scale_with_vote = float(scale_with_conf) * vote_scaler
                # print(scale_with_vote)
                final_sent = 1.0 * float(scale_with_vote)
                # print(final_sent)
                pos = pos + final_sent

print(pos)
print(neg)



