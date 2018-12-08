import sqlite3

conn = sqlite3.connect("sentiments.db")
conn.execute("CREATE TABLE IF NOT EXISTS histories(id integer, screenname text, positive float, negative float, neutral float, transacted datetime default CURRENT_TIMESTAMP, flag text)")
conn.execute("CREATE TABLE IF NOT EXISTS users(id integer primary key AUTOINCREMENT not null, username text not null, hash text not null)")
conn.execute("CREATE UNIQUE INDEX username ON users(username)")
conn.commit()
conn.close()