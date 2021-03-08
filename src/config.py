def getconfig(conn):
    cfg = {}
    cur = conn.cursor()

    cur.execute("SELECT * FROM `config`")

    for row in cur.fetchall():
        cfg[row['key']] = row['value']
    
    return cfg