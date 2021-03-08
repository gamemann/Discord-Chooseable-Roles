import os
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
        # Add Discord role to manage commands.
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
            
    
    client.run(cfg["BotToken"])