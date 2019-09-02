from user_definition import sql_conn_string
import psycopg2
conn = psycopg2.connect(sql_conn_string)
print("Database connected successfully")
cur = conn.cursor()

cmds = ["""
select * from products limit 10;
"""]

for c in cmds:
    try:
        cur.execute(c)
        rows = cur.fetchall()
        for data in rows:
            print([str(d) for d in data])
        conn.commit()
    except psycopg2.ProgrammingError:
        print("""CAUTION FAILED: '%s' """ % c)
        conn.rollback()
