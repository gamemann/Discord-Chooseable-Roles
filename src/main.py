# One of my first Python projects \O/.
import sys

import config
import discordbot
import db
import setup

def main():
    # Set default values for CFG file and SQLite databse locations.
    cfgfile = "/etc/dcr/settings.json"
    sqlitedb = "/etc/dcr/dcr.db"

    # Loop through all arguments.
    for arg in sys.argv:
        # Handle config file.
        if arg.startswith("cfg="):
            cfgfile = arg.split('=')[1]
        elif arg.startswith("sqlite="):
            sqlitedb = arg.split('=')[1]
        
    # Now connect to SQLite.
    conn = db.connect(sqlitedb)

    # Attempt to setup tables if they aren't already along with get information.
    setup.setuptables(conn)

    # Get config from JSON file.
    cfg = config.getconfig(cfgfile)

    # Connect Discord bot.
    discordbot.connect(cfg, conn)

if __name__ == "__main__":
    main()