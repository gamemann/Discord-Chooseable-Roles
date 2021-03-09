import os
import base64
import discord
from discord.ext import commands

import permissions

def connect(cfg, conn):
    bot = commands.Bot(command_prefix='!')

    @bot.event
    async def on_ready():
        print("Successfully connected to Discord.")

    @bot.command()
    async def dcr_addrole(ctx, name=None):
        msg = ctx.message

        roles = permissions.getroles(conn, msg.guild.id)

        # Ensure they have permission and check name argument.
        if not permissions.hasperm(conn, roles, msg.author):
            return

        if name == None:
            await msg.channel.send("You did not supply a role to add.")
            return
        
        role = discord.utils.get(msg.guild.roles, name=name)

        if role.id in roles:
            await msg.channel.send("Role already allowed.")
            return

        # Add role.
        err = permissions.addrole(conn, msg.guild.id, role.id)

        if err:
            await msg.channel.send("Did not add role successfully (Err # => " + str(err) + ").")
        else:
            await msg.channel.send("**Successfully** added role!")

    @bot.command()
    async def dcr_delrole(ctx, name=None):
        msg = ctx.message

        roles = permissions.getroles(conn, msg.guild.id)
        
        # Ensure they have permission and check name argument.
        if not permissions.hasperm(conn, roles, msg.author):
            return

        if name == None:
            await msg.channel.send("You did not supply a role to remove.")
            return

        role = discord.utils.get(msg.guild.roles, name=name)

        if role.id not in roles:
            await msg.channel.send("Role already isn't allowed.")
            return

        # Delete role.
        err = permissions.delrole(conn, msg.guild.id, role.id)

        if err:
            await msg.channel.send("Did not delete role successfully (Err # => " + str(err) + ").")
        else:
            await msg.channel.send("**Successfully** deleted role!")

    @bot.command()
    async def dcr_listroles(ctx):
        msg = ctx.message

        roles = permissions.getroles(conn, msg.guild.id)
        
        if not permissions.hasperm(conn, roles, msg.author):
            return

        tosend = "**Allowed roles**\n"

        for roleid in roles:
            role = discord.utils.get(msg.guild.roles, id=roleid)
            tosend = tosend + "- " + role.name + "\n"

        await msg.channel.send(tosend)

    @bot.event
    async def on_raw_reaction_add(pl):
        server = discord.utils.get(bot.guilds, id=pl.guild_id)
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
        
        await bot.add_roles(pl.member, role)

    @bot.event
    async def on_raw_reaction_remove(reaction, user):
        server = discord.utils.get(bot.guilds, id=pl.guild_id)
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
        
        await bot.remove_roles(pl.member, role)
            
    
    bot.run(cfg['BotToken'])