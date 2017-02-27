
def receive_queue(mysql_info, tablename, username, status):
    import mysql.connector
    cnx = mysql.connector.connect(**mysql_info)
    x = cnx.cursor()
    if status < 0:
        query = "SELECT * FROM {} WHERE user='{}' ORDER BY status ASC, id ASC;".format(tablename, username)
    else:
        query = "SELECT * FROM {} WHERE user='{}' AND status='{}' ORDER BY id ASC".format(tablename, username, status)
    x.execute(query,)
    elements = []
    for (id, user, execution_file, workflow_json, status, progress, original_workflow_file, sending_date, finished_date, priority, output_file) in x:
        subdict = {
            "id" : id,
            "user": user,
            "execution_file": execution_file,
            #"workflow_json": workflow_json, //We'll leave this out for now... this just blows up the size and harms readability for debugging
            "status": status,
            "progress": progress,
            "original_workflow_file": original_workflow_file,
            "sending_date": str(sending_date),      #I have a dream! I have a dream that one day all nations will rise up, 
            "finished_date": str(finished_date),    #and live out the true meaning of unified date formatting! 
                                                    #'We hold these truths to be self-evident: that all dates are created equal!'
            "priority": priority,
            "output_file": output_file
        }
        elements.append(subdict)
    return elements

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='This script receives the workflow queue for a user.')
    parser.add_argument("-mysqlhost", "--mh", type=str, help="The host of the mysql database")
    parser.add_argument("-mysqluser", "--mu", type=str, help="The user of the mysql database")
    parser.add_argument("-mysqlpw", "--pw", type=str, help="The pw of the user of the mysql database")
    parser.add_argument("-mysqldb", "--db", type=str, help="The mysql database")
    parser.add_argument("-mysqltable", "--tbl", type=str, help="The table in the mysql database containing all the queue items")
    parser.add_argument("-username", "--us", type=str, help="The username for which all queue items shall be retrieved")
    parser.add_argument("-status", "--s", type=str, help="The status to filter (no filter if not set)")
    args, leftovers = parser.parse_known_args()
    
    mysql_info = {
        "host": args.mh,
        "user": args.mu,
        "password": args.pw,
        "database": args.db
    }
    tablename = args.tbl
    username = args.us
    status = -1
    if args.s is not None:
        status = args.s
    val = receive_queue(mysql_info, tablename, username, status)
    print(val)

