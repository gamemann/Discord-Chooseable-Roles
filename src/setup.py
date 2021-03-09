import fileinput
import sys
import sqlite3

def setuptables(conn):
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS `reactionroles` (id integer PRIMARY KEY AUTOINCREMENT, msgid integer, guildid integer, reaction text, roleid integer)")
    cur.execute("CREATE TABLE IF NOT EXISTS `messages` (id integer PRIMARY KEY, guildid integer, maxreactions integer, contents text)")
    cur.execute("CREATE TABLE IF NOT EXISTS `config` (key text PRIMARY KEY, value text)")
    cur.execute("CREATE TABLE IF NOT EXISTS `permissions` (guildid integer PRIMARY KEY, roles text)")

    conn.commit()

    print("[SETUP] Created all tables.")

def setupcfg(conn):
    cur = conn.cursor()
    i = 0

    print("Bot Token: ")

    for value in sys.stdin:
        # Bot Token
        if i == 0:
            cur.execute("INSERT OR REPLACE INTO `config` (`key`, `value`) VALUES ('BotToken', ?)", (value,))
            conn.commit()
            print("Successfully updated Bot Token.\n")
            print("Client ID: ")
        # Client ID
        elif i == 1:
            cur.execute("INSERT OR REPLACE INTO `config` (`key`, `value`) VALUES ('ClientID', ?)", (value,))
            conn.commit()
            print("Successfully updated Client ID.\n")
            print("Client Secret: ")
        elif i == 2:
            cur.execute("INSERT OR REPLACE INTO `config` (`key`, `value`) VALUES ('ClientSeceret', ?)", (value,))
            conn.commit()
            print("Successfully updated Client Secret.")
            break
        else:
            break
        
        i = i + 1
        pass


