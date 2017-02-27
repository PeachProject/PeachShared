def remove_queue_item(mysql_info, tablename, index, username_check):
    import mysql.connector
    cnx = mysql.connector.connect(**mysql_info)
    x = cnx.cursor()
    query = "DELETE FROM {} WHERE id='{}'".format(tablename, index)
    x.execute(query,)
    cnx.commit()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='This script receives the workflow queue for a user.')
    parser.add_argument("-mysqlhost", "--mh", type=str, help="The host of the mysql database")
    parser.add_argument("-mysqluser", "--mu", type=str, help="The user of the mysql database")
    parser.add_argument("-mysqlpw", "--pw", type=str, help="The pw of the user of the mysql database")
    parser.add_argument("-mysqldb", "--db", type=str, help="The mysql database")
    parser.add_argument("-mysqltable", "--tbl", type=str, help="The table in the mysql database containing all the queue items")
    parser.add_argument("-index", "--id", type=str, help="The id of the row that should be deleted.")
    parser.add_argument("-username", "--us", type=str, help="The queue item that will be deleted has to belong to the given user for safety reasons.")
    args = parser.parse_args()
    mysql_info = {
        "host": args.mh,
        "user": args.mu,
        "password": args.pw,
        "database": args.db
    }
    tablename = args.tbl
    index = args.id
    user = args.us
    remove_queue_item(mysql_info, tablename, index, user)
    print(">>> Removed row with id '{}'".format(index))