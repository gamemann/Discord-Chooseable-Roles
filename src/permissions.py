import json

def hasperm(conn, roles, user):
    hasperm = False

    userroles = user.roles

    for role in userroles:
        if role.id in roles:
            hasperm = True

    if not hasperm:
        # Check to see if they're the owner of guild.
        if user.id == user.guild.owner_id:
            hasperm = True

    return hasperm

def addrole(conn, guildid, role):
    cur = conn.cursor()

    cur.execute("SELECT `roles` FROM `permissions` WHERE `guildid`=?", (guildid,))
    conn.commit()

    # Fetch the results, deserialize JSON, add role, and serialize/update.
    results = "{\"roles\": []}"
    query = cur.fetchone()

    if query != None and len(query) > 0:
        results = query['roles']

    roles = json.loads(results)

    # Ensure the role doesn't exist.
    if role not in roles['roles']:
        roles['roles'].append(role)
        
    rolesjson = json.dumps(roles)

    cur.execute("INSERT OR REPLACE INTO `permissions` (`guildid`, `roles`) VALUES (?, ?)", (guildid, rolesjson))
    conn.commit()

    if cur.rowcount > 0:
        return 0
    else:
        return 1

def delrole(conn, guildid, role):
    cur = conn.cursor()

    cur.execute("SELECT `roles` FROM `permissions` WHERE `guildid`=?", (guildid,))
    conn.commit()

    # Fetch the results, deserialize JSON, add role, and serialize/update.
    results = cur.fetchone()

    if results == None or len(results) < 1:
        return 1

    roles = json.loads(results['roles'])

    # Check if the role does indeed exist.
    if role in roles['roles']:
        roles['roles'].remove(role)

    rolesjson = json.dumps(roles)

    cur.execute("INSERT OR REPLACE INTO `permissions` (`guildid`, `roles`) VALUES (?, ?)", (guildid, rolesjson))
    conn.commit()

    if cur.rowcount > 0:
        return 0
    else:
        return 1

def getroles(conn, guildid):
    roles = {}
    roles['roles'] = []
    cur = conn.cursor()

    cur.execute("SELECT `roles` FROM `permissions` WHERE `guildid`=?", (guildid,))
    conn.commit()

    results = cur.fetchone()

    if results != None and len(results) > 0:
        roles = json.loads(results['roles'])

    return roles['roles']