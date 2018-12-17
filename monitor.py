import time
import datetime
import psutil
import logging
import MySQLdb

LOG_FILE = 'monitor.log'
image_file = 'monitor.png'

db = MySQLdb.connect(host='localhost',
                     user='root',
                     passwd='pun15h3r',
                     db='dream')

cur = db.cursor()

TABLE = dict()

TABLE['bandwidth_monitor'] = (
    "CREATE TABLE bandwidth_monitor("
    "date_time TIMESTAMP DEFAULT 0,"
    "data_used INT);"
)


def main():
    # calling the function to log the data
    global new_value
    setup_logging()
    value = 0
    table_name = list()
    for tables in TABLE:
        name = tables
        table_name.append(name)
    while True:
        try:
            #  lets stream the upload and download data in bytes
            bytes_sent, bytes_recv = psutil.net_io_counters().bytes_sent, psutil.net_io_counters().bytes_recv

            new_value = bytes_recv + bytes_sent

        # after viewing lets log the data into the log file
        except ValueError as err:  # when an error occurs the file should log the data in
            logging.info(err)

        if value:  # else we substitute the old_values from the new ones then append and log the data
            new_data = new_value - value

            logging.info(new_data)

            if value:  # if the value is still true i need it to record to the database
                try:
                    list_data = [new_data]
                    time_logged = datetime.datetime.now()
                    cur.execute("INSERT INTO {} VALUES(%s, %s)".format(table_name[0]), (time_logged, list_data))
                    db.commit()
                except MySQLdb.Error as err:
                    print("Table does not exist:\n Attempting to Creat Table {}".format(table_name[0]), ":\n"
                                                                                                        "=========================>")
                    make_data_tables()
                    print("DONE")


        value = new_value

        time.sleep(1)  # lets break for a second before looping again


def setup_logging():
    # our basic configuration for the log file

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format=" %(message)s",
    )


def make_data_tables():
    # creating database tables if they dont exist
    # for values named in TABLE use them to create the table in the data base to insert the results
    for table_name in TABLE:
        table_description = TABLE[table_name]
        try:
            print("Creating table {}:".format(table_name)),
            cur.execute(table_description)
        except MySQLdb.Error as err:
            print("Exiting with error {}:".format(err))
            exit(1)
        else:
            print(" ******\n OK\n Table {} created successful".format(table_name))
            db.commit()


if __name__ == '__main__':
    main()