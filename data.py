import sqlite3 as lite
import scraper
import threading

class PhoneDataLayer:
    def __init__(self, db='numbers.db'):
        self.lock = threading.Lock()
        con = None
        try:
            con = lite.connect(db)
            with con:
                cur = con.cursor()
                cur.execute("DROP TABLE IF EXISTS Numbers")
                cur.execute("CREATE TABLE Numbers(number TEXT primary key not null, count INT, comment TEXT, date TEXT)")
        except lite.Error, e:
            raise e
        finally:
            if con:
                con.close()

    def insert_entries(self, entries):
        con = lite.connect('numbers.db')
        with con:
            cur = con.cursor()
            for entry in entries:
                cur.execute('INSERT OR REPLACE INTO Numbers(number, count, comment, date) VALUES (?, ?, ?, CURRENT_TIMESTAMP);', [entry.phone_number, entry.report_count, entry.comment])
        con.close()

    def get_all_entries(self):
        parser  = scraper.Parser(scraper.ValidUAOpener().open(scraper.PHONE_SITE).read())
        entries = parser.parse()
        self.insert_entries(entries)
        con  = lite.connect('numbers.db')
        rows = None
        with con:
            cur = con.cursor()
            cur.execute('SELECT * FROM Numbers ORDER BY date;')
            rows = cur.fetchall()

        entries = []
        for row in rows:
            entries[len(entries):] = [scraper.PhoneNumberEntry(row[0], row[1], row[2])]

        con.close()
        return entries

    def get_db_entries(self, n=60):
        con  = lite.connect('numbers.db')
        rows = None
        with con:
            cur = con.cursor()
            cur.execute('SELECT * FROM Numbers ORDER BY date LIMIT {}'.format(n))
            rows = cur.fetchall()

        entries = []
        for row in rows:
            entries[len(entries):] = [scraper.PhoneNumberEntry(row[0], row[1], row[2])]

        con.close()
        return entries

    def get_entries(self, n=None):

        if n is not None:
            if n <= 0:
                return None

        parser  = scraper.Parser(scraper.ValidUAOpener().open(scraper.PHONE_SITE).read())
        entries = parser.parse()
        self.insert_entries(entries)

        if n is None:
            return entries
        elif n < len(entries):
            return entries[:n]
        else:
            retVal = self.get_db_entries(n)
            return retVal
