import logging
import psycopg2
import os


logger = logging.getLogger("Gateway")
habr_tab = '''CREATE TABLE IF NOT EXISTS links (
    link VARCHAR PRIMARY KEY
    )'''


class DB:
    def __init__(self, sender=None):
        self.sender = sender
        self.url = os.environ['DATABASE_URL']
        self.conn = self.connect()
        self.create_tab()

    def connect(self):
        try:
            conn = psycopg2.connect(self.url, sslmode='require')
        except Exception as e:
            self.error_log('db connect error {}'.format(e))
        else:
            self.info_log('Success DB connection')
            return conn

    def reconnect(self):
        self.info_log('db reconnect')
        if self.conn:
            self.conn.close()
        self.conn = None
        self.conn = self.connect()

    def create_tab(self):
        self.cursor_execute(habr_tab)

    # ---------------- requests -------------------

    def insert(self, link):
        query = "INSERT INTO links (link) values('{0}') ON CONFLICT DO NOTHING".\
            format(link)
        return self.cursor_execute(query)

    # ----------------- logging --------------------

    def log_sender(self, msg):
        print(msg)
        if self.sender:
            self.sender.debug(msg)

    def info_log(self, msg):
        logger.info(msg)
        self.log_sender('Gateway: Info - {}'.format(msg))

    def error_log(self, msg):
        logger.error(msg)
        self.log_sender('Gateway: Error - {}'.format(msg))

        # -------------------execute----------------------

    def cursor_execute(self, query, err_count=0):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
        except Exception as e:
            self.error_log('execute query error (try {}): {}'.format(err_count + 1, e))
            if err_count < 1:
                self.reconnect()
                self.cursor_execute(query, err_count + 1)
        else:
            self.conn.commit()
            return cur.fetchall() if cur.description else cur.statusmessage


# db = DB()
# links = ['https://habr.com/ru/post/470267/', 'https://habr.com/ru/post/470113/', 'https://habr.com/ru/post/469995/', 'https://habr.com/ru/post/470035/', 'https://habr.com/ru/post/470023/', 'https://habr.com/ru/post/464181/', 'https://habr.com/ru/company/ruvds/blog/468237/', 'https://habr.com/ru/post/469917/', 'https://habr.com/ru/company/microsoft/blog/469077/', 'https://habr.com/ru/post/469839/', 'https://habr.com/ru/post/469753/', 'https://habr.com/ru/post/469723/', 'https://habr.com/ru/post/469577/', 'https://habr.com/ru/company/microsoft/blog/469079/', 'https://habr.com/ru/post/469345/', 'https://habr.com/ru/post/469259/', 'https://habr.com/ru/post/469093/', 'https://habr.com/ru/company/ruvds/blog/468235/', 'https://habr.com/ru/post/467665/']
# for link in links:
#     print(db.insert(link, 123))
