import os
import base64
import discord

import permissions

def connect(cfg, conn):
    client = discord.Client()

    @client.event
    async def on_ready():
        print("Successfully connected to Discord.")

    @client.event
    async def on_message(msg):
        # Ignore messages from the bot itself.
        if msg.author == client.user:
            return

        # Check for permission.
        roles = permissions.getroles(conn, msg.guild.id)
        if not permissions.hasperm(conn, roles, msg.author):
            return
        
        # Add Discord role to manage commands.
        if msg.content.startswith("/dcr_addrole"):
            args = msg.content.split()

            if len(args) < 2:
                await msg.channel.send("You did not supply a role to add.")
            else:
                role = discord.utils.get(msg.guild.roles, name=args[1])

                if role.id in roles:
                    await msg.channel.send("Role already allowed.")
                    return

                err = permissions.addrole(conn, msg.guild.id, role.id)

                if err:
                    await msg.channel.send("Did not add role successfully (Err # => " + str(err) + ").")
                else:
                    await msg.channel.send("**Successfully** added role!")
        # Remove role from allowed list.
        if msg.content.startswith("/dcr_delrole"):
            args = msg.content.split()

            if len(args) < 2:
                await msg.channel.send("You did not supply a role to delete/remove.")
            else:
                role = discord.utils.get(msg.guild.roles, name=args[1])

                if role.id not in roles:
                    await msg.channel.send("Role already isn't allowed.")
                    return

                err = permissions.delrole(conn, msg.guild.id, role.id)

                if err:
                    await msg.channel.send("Did not delete role successfully (Err # => " + str(err) + ").")
                else:
                    await msg.channel.send("**Successfully** deleted role!")
        # List allowed roles.
        elif msg.content.startswith("/dcr_listroles"):
            tosend = "**Allowed roles**\n"

            for roleid in roles:
                role = discord.utils.get(msg.guild.roles, id=roleid)
                tosend = tosend + "- " + role.name + "\n"

            await msg.channel.send(tosend)

    @client.event
    async def on_raw_reaction_add(pl):
        server = discord.utils.get(client.guilds, id=pl.guild_id)
        chnl = discord.utils.get(server.channels, id=pl.channel_id)

        # Get Base64 of Emoji.
        name = base64.b64encode(pl.emoji.name.encode()).decode("utf-8")

        # Get cursor.
        cur = conn.cursor()

        # Execute query.
        cur.execute("SELECT `roleid` FROM `reactionroles` WHERE `msgid`=? AND `guildid`=? AND `reaction`=?", (pl.message_id, pl.guild_id, str(name)))

        results = cur.fetchone()

        if results == None or len(results) < 1:
            return

        role = discord.utils.get(msg.guild.roles, id=results['roleid'])
        
        await client.add_roles(pl.member, role)

    @client.event
    async def on_raw_reaction_remove(reaction, user):
        server = discord.utils.get(client.guilds, id=pl.guild_id)
        chnl = discord.utils.get(server.channels, id=pl.channel_id)

        # Get Base64 of Emoji.
        name = base64.b64encode(pl.emoji.name.encode()).decode("utf-8")

        # Get cursor.
        cur = conn.cursor()

        # Execute query.
        cur.execute("SELECT `roleid` FROM `reactionroles` WHERE `msgid`=? AND `guildid`=? AND `reaction`=?", (pl.message_id, pl.guild_id, str(name)))

        results = cur.fetchone()

        if results == None or len(results) < 1:
            return

        role = discord.utils.get(msg.guild.roles, id=results['roleid'])
        
        await client.remove_roles(pl.member, role)
            
    
    client.run(cfg['BotToken'])