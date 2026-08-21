from database import get_connection
conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT id, site_id, visit_date, comment, visit_time FROM feedback ORDER BY id DESC LIMIT 3;")
for row in cur.fetchall():
    print(row)
