# One of my first Python projects \O/.
import sys

import config
import discordbot
import db
import setup

def main():
    # Now connect to SQLite.
    conn = db.connect()

    # Attempt to setup tables if they aren't already along with get information.
    if len(sys.argv) > 1 and str(sys.argv[1]) == "setup":
        setup.setuptables(conn)

        if len(sys.argv) < 3 or (len(sys.argv) > 2 and str(sys.argv[2]) != "skipcfg"):
            setup.setupcfg(conn)

    # Get config from database.
    cfg = config.getconfig(conn)

    # Connect Discord bot.
    discordbot.connect(cfg, conn)

if __name__ == "__main__":
    main()