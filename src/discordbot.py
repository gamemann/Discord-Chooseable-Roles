import os
import base64
import time

import discord
from discord.ext import commands

import permissions
import db

bot = commands.Bot(command_prefix='!')
cooldown = {}

async def handlecooldown(userid, cfg, guild):
    # Check cooldown for specific user. If they don't exist, create new element in cooldown for the user doing `curtime + cooldowntime` as value.
    if cooldown != None and cooldown.get(userid, None) != None and cooldown[userid] > int(time.time()):
        user = await guild.fetch_member(userid)
        timetowait = cooldown[userid] - int(time.time())
        await user.send("Please wait **" + str(int(timetowait)) + "** seconds before adding or removing another reaction.")
        return 1
    else:
        cooldown[userid] = int(time.time()) + cfg["Cooldown"]

    return 0

def connect(cfg, conn):
    # Enable intents.
    intents = discord.Intents.default()
    intents.members = True 
    
    # Get connection cursor.
    cur = conn.cursor()

    @bot.event
    async def on_ready():
        print("Successfully connected to Discord.")

    @bot.command()
    async def dcr_addrole(ctx, name=None):
        usage = "**Usage** - !dcr_addrole <role name>"
        msg = ctx.message

        roles = permissions.getroles(conn, msg.guild.id)

        # Ensure they have permission and check name argument.
        if not permissions.hasperm(conn, roles, msg.author):
            return

        if name == None:
            await msg.channel.send(usage + "\n\nError - You did not supply a role to add.", delete_after=cfg["BotMsgStayTime"])

            return
        
        role = discord.utils.get(msg.guild.roles, name=name)

        # Check role.
        if role == None:
            await ctx.channel.send("Could not find role specified.")

            return

        # Ensure role isn't already allowed.
        if role.id in roles:
            await msg.channel.send("Role already allowed.", delete_after=cfg["BotMsgStayTime"])

            return

        # Add role.
        err = permissions.addrole(conn, msg.guild.id, role.id)

        if err:
            await msg.channel.send("Did not add role successfully (Err # => " + str(err) + ").", delete_after=cfg["BotMsgStayTime"])
        else:
            await msg.channel.send("**Successfully** added role!", delete_after=cfg["BotMsgStayTime"])

    @bot.command()
    async def dcr_delrole(ctx, name=None):
        usage = "**Usage** - !dcr_delrole <role name>"
        msg = ctx.message

        roles = permissions.getroles(conn, msg.guild.id)
        
        # Ensure they have permission and check name argument.
        if not permissions.hasperm(conn, roles, msg.author):
            return

        if name == None:
            await msg.channel.send(usage + "\n\nError - You did not supply a role to remove.", delete_after=cfg["BotMsgStayTime"])

            return

        role = discord.utils.get(msg.guild.roles, name=name)

        # Check role.
        if role == None:
            await ctx.channel.send("Could not find role specified.")

            return

        # Ensure role isn't already not allowed.
        if role.id not in roles:
            await msg.channel.send("Role already isn't allowed.", delete_after=cfg["BotMsgStayTime"])

            return

        # Delete role.
        err = permissions.delrole(conn, msg.guild.id, role.id)

        if err:
            await msg.channel.send("Did not delete role successfully (Err # => " + str(err) + ").", delete_after=cfg["BotMsgStayTime"])
        else:
            await msg.channel.send("**Successfully** deleted role!", delete_after=cfg["BotMsgStayTime"])

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

        await msg.channel.send(tosend, delete_after=cfg["BotMsgStayTime"])

    @bot.command()
    async def dcr_addmsg(ctx, maxreactions=1, contents=""):
        msg = ctx.message

        roles = permissions.getroles(conn, msg.guild.id)

        # Ensure they have permission and check name argument.
        if not permissions.hasperm(conn, roles, msg.author):
            return

        # Add message to current channel.
        newmsg = await ctx.channel.send(contents.replace(r'\n', '\n'))

        cur.execute("INSERT INTO `messages` (`msgid`, `guildid`, `maxreactions`, `contents`) VALUES (?, ?, ?, ?)", (newmsg.id, ctx.guild.id, maxreactions, contents))
        conn.commit()

    @bot.command()
    async def dcr_editmsg(ctx, msgid=None, maxreactions=None, contents=None):
        # Check arguments and ensure they're all valid.
        usage = "**Usage**: !dcr_editmsg <msgid> <maxreactions=None> <contents=None>."
        
        if msgid == None:
            await ctx.channel.send(usage + "\n\nError - Please specify a message ID to edit.", delete_after=cfg["BotMsgStayTime"])

            return

        # Retrieve message by ID.
        try:
            msg = await ctx.fetch_message(msgid)
        except NotFound:
            await ctx.channel.send("Message ID not found inside of guild.", delete_after=cfg["BotMsgStayTime"])

            return

        # Initialize setparams and set our where clauses.
        setparams = {}
        whereparams = {"msgid": msgid, "guildid": ctx.guild.id}
        
        # Check max reactions.
        if maxreactions != None and maxreactions != "SKIP":
            setparams["maxreactions"] = maxreactions

        # Check contents.
        if contents != None and contents != "SKIP":
            setparams["contents"] = str(contents)
            await msg.edit(content=contents.replace(r'\n', '\n'))

        # Use our helper function to update the row inside of the messages table.
        db.updateoptional(conn, "messages", setparams, whereparams)

        await ctx.channel.send("Updated message **successsfully**!", delete_after=cfg["BotMsgStayTime"])

    @bot.command()
    async def dcr_delmsg(ctx, msgid=None):
        # Check arguments and ensure they're all valid.
        usage = "**Usage**: !dcr_delmsg <msgid>."

        if msgid == None:
            await ctx.channel.send(usage + "\n\nError - Please specify a message ID to edit.", delete_after=cfg["BotMsgStayTime"])

            return

        # Retrieve message by ID.
        try:
            msg = await ctx.fetch_message(msgid)
        except NotFound:
            await ctx.channel.send("Message ID not found inside of guild.", delete_after=cfg["BotMsgStayTime"])

            return

        # Delete message from messages table.
        cur.execute("DELETE FROM `messages` WHERE `msgid`=? AND `guildid`=?", (msg.id, ctx.guild.id))
        conn.commit()

        # Remove the message from the Discord channel itself.
        await msg.delete()

        await ctx.channel.send("Deleted message **successsfully**!", delete_after=cfg["BotMsgStayTime"])

    @bot.command()
    async def dcr_addreaction(ctx, msgid=None, reaction=None, rolename=None):
        # Check arguments and ensure they're all valid.
        usage = "**Usage** - !dcr_addreaction <msgid> <reaction> <role name>."

        if msgid == None:
            await ctx.channel.send(usage + "\n\n**Error** - Please specify a message ID to add the reaction to.", delete_after=cfg["BotMsgStayTime"])

            return

        if reaction == None:
            await ctx.channel.send(usage + "\n\n**Error** - Please specify a reaction to add.", delete_after=cfg["BotMsgStayTime"])

            return

        if rolename == None:
            await ctx.channel.send(usage + "\n\n**Error** - Please specify a role name for the user to retrieve on reaction.", delete_after=cfg["BotMsgStayTime"])

            return
        
        # Retrieve message by ID.
        try:
            msg = await ctx.fetch_message(msgid)
        except NotFound:
            await ctx.channel.send("Message ID not found inside of guild.", delete_after=cfg["BotMsgStayTime"])

            return

        # Convert emoji into acceptable text.
        name = base64.b64encode(reaction.encode()).decode("utf-8")

        # Get role so we can insert by ID.
        role = discord.utils.get(ctx.guild.roles, name=rolename)

        # Insert or replace into database.
        cur.execute("INSERT OR REPLACE INTO `reactionroles` (`msgid`, `guildid`, `reaction`, `roleid`) VALUES (?, ?, ?, ?)", (msgid, ctx.guild.id, str(name), role.id))
        conn.commit()

        # Add reaction to message.
        await msg.add_reaction(reaction)

        await ctx.channel.send("**Successfully** added reaction.", delete_after=cfg["BotMsgStayTime"])

    @bot.command()
    async def dcr_delreaction(ctx, msgid=None, reaction=None):
        # Check arguments and ensure they're all valid.
        usage = "**Usage** - !dcr_delreaction <msgid> <reaction>."

        if msgid == None:
            await ctx.channel.send(usage + "\n\n**Error** - Please specify a message ID to delete the reaction from.", delete_after=cfg["BotMsgStayTime"])

            return

        if reaction == None:
            await ctx.channel.send(usage + "\n\n**Error** - Please specify a reaction to delete.", delete_after=cfg["BotMsgStayTime"])

            return
        
        # Retrieve message by ID.
        try:
            msg = await ctx.fetch_message(msgid)
        except NotFound:
            await ctx.channel.send("Message ID not found inside of guild.", delete_after=cfg["BotMsgStayTime"])

            return

        # Convert emoji into acceptable text.
        name = base64.b64encode(reaction.encode()).decode("utf-8")

        # Delete reaction definition from database.
        cur.execute("DELETE FROM `reactionroles` WHERE `msgid`=? AND `guildid`=? AND `reaction`=?", (msgid, ctx.guild.id, str(name)))
        conn.commit()

        # Add reaction to message.
        await msg.remove_reaction(reaction, bot.user)

        await ctx.channel.send("**Successfully** removed reaction.", delete_after=cfg["BotMsgStayTime"])

    @bot.event
    async def on_raw_reaction_add(pl):
        # Check to ensure reaction user isn't the bot itself.
        if pl.user_id == bot.user.id:
            return

        guild = await bot.fetch_guild(pl.guild_id)

        # Check guild.
        if guild == None:
            print("on_raw_reaction_add() :: Could not find guild with ID #" + str(pl.guild_id))

            return

        chnl = bot.get_channel(pl.channel_id)

        # Check channel.
        if chnl == None:
            print("on_raw_reaction_add() :: Could not find channel with ID #" + str(pl.channel_id))

            return
        
        msg = await chnl.fetch_message(pl.message_id)

        # Check message.
        if msg == None:
            print("on_raw_reaction_add() :: Could not find message with ID #" + str(pl.message_id))

            return

        user = await guild.fetch_member(pl.user_id)

        # Check user.
        if user == None:
            print("on_raw_reaction_add() :: Could not find user with ID #" + str(pl.user_id))

            return

        # Handle cooldown.
        if await handlecooldown(pl.user_id, cfg, guild):
            await msg.remove_reaction(pl.emoji.name, user)

            return

        # Ensure we aren't reaching the max reactions.
        reactions = 1
        maxreactions = 1

        cur.execute("SELECT COUNT(*) as count FROM `reactions` WHERE `userid`=? AND `msgid`=? AND `guildid`=?", (user.id, msg.id, guild.id))
        conn.commit()
        
        results = cur.fetchone()
        
        if results != None and len(results) > 0:
            reactions = results['count'] + 1

        cur.execute("SELECT `maxreactions` FROM `messages` WHERE `msgid`=? AND `guildid`=?", (msg.id, guild.id))
        conn.commit()

        results = cur.fetchone()

        if results != None and len(results) > 0:
            maxreactions = results['maxreactions']

        if reactions > maxreactions:
            # Remove reaction.
            await msg.remove_reaction(pl.emoji.name, user)

            # DM user.
            await user.send("You've reached the maximum reactions for this message/type (" + str(reactions) + "/" + str(maxreactions) + ")")

            return

        # Get Base64 of Emoji.
        name = base64.b64encode(pl.emoji.name.encode()).decode("utf-8")

        # Execute query.
        cur.execute("SELECT `roleid` FROM `reactionroles` WHERE `msgid`=? AND `guildid`=? AND `reaction`=?", (pl.message_id, pl.guild_id, str(name)))
        conn.commit()

        results = cur.fetchone()

        if results == None or len(results) < 1:
            return

        # Retrieve role and ensure it exist.
        role = discord.utils.get(msg.guild.roles, id=results['roleid'])

        if role == None:
            print("Failed to find role with ID #" + str(results['roleid']))

            return
        
        await pl.member.add_roles(role)

        # Insert reaction into database.
        cur.execute("INSERT OR REPLACE INTO `reactions` (`userid`, `msgid`, `guildid`, `reaction`) VALUES (?, ?, ?, ?)", (user.id, msg.id, guild.id, str(name)))
        conn.commit()

    @bot.event
    async def on_raw_reaction_remove(pl):
        if pl.user_id == bot.user.id:
            return

        guild = await bot.fetch_guild(pl.guild_id)

        # Check guild.
        if guild == None:
            print("on_raw_reaction_remove() :: Could not find guild with ID #" + str(pl.guild_id))

            return

        chnl = bot.get_channel(pl.channel_id)

        # Check channel.
        if chnl == None:
            print("on_raw_reaction_remove() :: Could not find channel with ID #" + str(pl.channel_id))

            return
        
        msg = await chnl.fetch_message(pl.message_id)

        # Check message.
        if msg == None:
            print("on_raw_reaction_remove() :: Could not find message with ID #" + str(pl.message_id))

            return

        user = await guild.fetch_member(pl.user_id)

        # Check user.
        if user == None:
            print("on_raw_reaction_remove() :: Could not find user with ID #" + str(pl.user_id))

            return

        # Get Base64 of Emoji.
        name = base64.b64encode(pl.emoji.name.encode()).decode("utf-8")

        # Delete reaction entry from database.
        cur.execute("DELETE FROM `reactions` WHERE `userid`=? AND `msgid`=? AND `guildid`=? AND `reaction`=?", (user.id, msg.id, guild.id, str(name)))
        conn.commit()

        # Execute query.
        cur.execute("SELECT `roleid` FROM `reactionroles` WHERE `msgid`=? AND `guildid`=? AND `reaction`=?", (pl.message_id, pl.guild_id, str(name)))
        conn.commit()

        results = cur.fetchone()

        if results == None or len(results) < 1:
            return

        role = discord.utils.get(msg.guild.roles, id=results['roleid'])
    
        # pl.member doesn't work with reaction remove event. Therefore, fetch it manually.
        guild = await bot.fetch_guild(pl.guild_id)
        member = await guild.fetch_member(pl.user_id)
        
        await member.remove_roles(role)
            
    
    bot.run(cfg['BotToken'])