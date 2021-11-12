import fileinput
import sys
import sqlite3

def setuptables(conn):
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS `reactions` (id integer PRIMARY KEY AUTOINCREMENT, userid integer, msgid integer, guildid integer, reaction text)")
    cur.execute("CREATE TABLE IF NOT EXISTS `reactionroles` (id integer PRIMARY KEY AUTOINCREMENT, msgid integer, guildid integer, reaction text, roleid integer)")
    cur.execute("CREATE TABLE IF NOT EXISTS `messages` (id integer PRIMARY KEY AUTOINCREMENT, msgid integer, guildid integer, maxreactions integer, contents text)")
    cur.execute("CREATE TABLE IF NOT EXISTS `permissions` (guildid integer PRIMARY KEY, roles text)")

    conn.commit()

    print("[SETUP] Created all tables.")