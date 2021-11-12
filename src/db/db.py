import sqlite3

def connect(location):
    conn = sqlite3.connect(location)
    conn.row_factory = sqlite3.Row

    return conn

def updateoptional(conn, table, setparams, whereparams):
    cur = conn.cursor()

    toset = []
    towhere = []
    values = []

    for key in setparams:
        toset.append(key + "=?")
        values.append(setparams[key])

    for key in whereparams:
        towhere.append(key + "=?")
        values.append(whereparams[key])

    setstr = ", ".join(toset)
    wherestr = "AND ".join(towhere)

    querystr = "UPDATE " + table + " SET " + setstr + " WHERE " + wherestr

    cur.execute(querystr, values)
    conn.commit()