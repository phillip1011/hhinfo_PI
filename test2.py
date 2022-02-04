import sqlite3


#def chkcard(uid):
    #relay.setup()
    #開啟資料庫連線
conn=sqlite3.connect("cardno.db")
c=conn.cursor()
c1=conn.cursor()

c.execute('DROP TABLE booking_histories')
conn.commit()
conn.close()