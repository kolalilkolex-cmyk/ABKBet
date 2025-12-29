import sqlite3
p=r'C:\Users\HP\OneDrive\Documents\ABKBet\instance\betting.db'
conn=sqlite3.connect(p)
cur=conn.cursor()
try:
    cur.execute("ALTER TABLE transactions ADD COLUMN payment_method VARCHAR(50)")
    conn.commit()
    print('ALTER TABLE applied: payment_method added')
except Exception as e:
    print('ALTER TABLE error:', e)
finally:
    conn.close()
