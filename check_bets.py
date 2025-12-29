import sqlite3

conn = sqlite3.connect('instance/betting.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM bets')
print(f'Total bets: {cursor.fetchone()[0]}')

cursor.execute("SELECT COUNT(*) FROM bets WHERE status='active'")
print(f'Active bets: {cursor.fetchone()[0]}')

cursor.execute('SELECT id, event_description, amount, status, created_at FROM bets ORDER BY created_at DESC LIMIT 5')
rows = cursor.fetchall()
print('\nRecent 5 bets:')
print('ID | Event | Amount | Status | Created')
print('-' * 100)
for r in rows:
    event = r[1][:50] if r[1] else 'N/A'
    print(f'{r[0]} | {event} | {r[2]} | {r[3]} | {r[4]}')

conn.close()
