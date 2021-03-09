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
    setup.setuptables(conn)

    # Get config from database.
    cfgfile = "/etc/dcr/settings.json"
    if len(sys.argv) > 1 and sys.argv[1].startswith("cfg="):
        cfgfile = sys.argv[1].split('=')[1]

    cfg = config.getconfig(cfgfile)

    # Connect Discord bot.
    discordbot.connect(cfg, conn)

if __name__ == "__main__":
    main()