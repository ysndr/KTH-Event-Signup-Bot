#! /usr/bin/env python3
from discord.ext.commands import Command, Bot, Context
from discord import Guild, Member, TextChannel, Role, PermissionOverwrite, Embed, Message, Client
import discord
import logging
import typing
import re
import os
import shlex
import argparse
import dotenv

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)


class KTHBot(Bot):
    setup_run = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

        guild = self.get_guild(int(os.getenv('DEB_GUILD')))

        self._manager_role = guild.get_role(int(os.getenv('DEB_MANAGER_ROLE')))
        self._signup_channel: TextChannel = guild.get_channel(
            int(os.getenv('DEB_SIGNUP_CHANNEL')))
        self._signup_emoji = os.getenv('DEB_EMOJI')
        self._n_participants = int(os.getenv('DEB_DEFAULT_SIZE'))

        self.setup_run = True

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.toggle_role(payload)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.toggle_role(payload)

    async def toggle_role(self, payload: discord.RawReactionActionEvent):
        guild: Guild = self.get_guild(payload.guild_id)

        if not self.setup_run \
                or payload.channel_id != self._signup_channel.id \
                or payload.emoji.name != self._signup_emoji:
            return

        channel = await self.fetch_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)

        member: discord.Member = await guild.fetch_member(payload.user_id)

        raw_id, raw_size = message.embeds[0].fields[-1].value[2:-2].split(',')
        size = int(raw_size)

        role_id = int(raw_id)
        await guild.fetch_roles()
        role: discord.Role = guild.get_role(role_id)

        if role in member.roles:
            await member.remove_roles(role)
        else:
            if len(role.members) < size + 1:  # -1 fo the bot itself
                await member.add_roles(role)
            else:
                await message.remove_reaction(self._signup_emoji, member)
        await guild.fetch_roles()
        participants_info = {
            "name": "Participants",
            "value": f"{len(role.members) -1}/{raw_size}"
        }
        if message.embeds[0].fields[-2].name == participants_info['name']:
            embed = message.embeds[0].set_field_at(
                index=-2, **participants_info)
        else:
            embed = message.embeds[0].insert_field_at(
                index=-1, **participants_info)
        await message.edit(embed=embed)

bot = KTHBot(command_prefix="$ ")

@bot.command(name="event")
async def event(ctx: Context, *args):
    if not ctx.bot.setup_run:
        await ctx.send("> not ready yet!")
        return

    if (ctx.author != ctx.guild.owner and ctx.bot._manager_role not in message.author.roles):
        return

    parser = ArgumentParser(prog="event", description='Create Event', add_help=False)
    parser.add_argument('--title', required=True,
                        dest='title', type=str, help='Event title')
    parser.add_argument('--size', dest='n_participants', default=ctx.bot._n_participants,
                        type=int, help='How many can participate in this event')
    try:
        parsed, description = parser.parse_known_args(args)
    except TypeError:
        text = parser.format_help()
        await ctx.send(text)
        return

    guild: Guild = ctx.guild

    signup_channel: TextChannel = ctx.bot._signup_channel
    root_category = signup_channel.category

    role = await guild.create_role(name=f"ep-{parsed.title}")
    event_channel = await guild.create_text_channel(
        parsed.title,
        category=root_category,
        overwrites={
            role: discord.PermissionOverwrite(read_messages=True),
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False),
            ctx.bot._manager_role: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
        })

    n_participants = parsed.n_participants

    embed = Embed()
    embed.title = parsed.title
    embed.add_field(name='Description', value=" ".join(
        description[1:]), inline=False)
    embed.set_author(name=ctx.author.display_name)
    embed.add_field(
        name='Meta', value=f"||{role.id},{n_participants}||", inline=True)

    signup_message: Message = await signup_channel.send(embed=embed)
    await signup_message.add_reaction(ctx.bot._signup_emoji)


@bot.command(name="edit")
async def edit(ctx: Context, *args):
    if not ctx.bot.setup_run:
        await ctx.send("> not ready yet!")
        return

    if (ctx.author != ctx.guild.owner and ctx.bot._manager_role not in message.author.roles):
        return

    parser = ArgumentParser(prog="edit", description='Create Event', add_help=False)
    parser.add_argument('--event', required=True, dest='event', type=int, help="Signup message id")
    parser.add_argument('--title', dest='title', type=str, help='Event title')
    parser.add_argument('--size', dest='n_participants',
                        type=int, help='How many can participate in this event')
    parser.add_argument('--description', dest='description',
                        type=str, help='description')
    try:
        parsed, description = parser.parse_known_args(args)
    except TypeError:
        text = parser.format_help()
        await ctx.send(text)
        return

    event_message = await ctx.bot._signup_channel.fetch_message(parsed.event)
    event_embed = event_message.embeds[0]
    description, participants, meta = event_embed.fields

    if parsed.title:
        event_embed.title = parsed.title
    if parsed.description:
        event_embed.set_field_at(index=0, inline=False,**{
            "name": "Description",
            "value": parsed.description,
        })
    if parsed.n_participants:
        role, _ = meta.value[2:][:-2].split(',')
        event_embed.set_field_at(index=1,**{
            "name": "Participants",
            "value": f"{participants.value.split('/')[1]}/{parsed.n_participants}"
        })
        event_embed.set_field_at(index=2, **{
            "name": "Meta",
            "value": f"||{role},{parsed.n_participants}||"
        })

    await event_message.edit(embed=event_embed)



class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        raise argparse.ArgumentError()

if __name__ == "__main__":
    bot.run(os.getenv('DEB_API_TOKEN'))
