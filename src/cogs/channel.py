import enum
import logging
import os
from typing import Literal

import coloredlogs
import disnake
from disnake.ext import commands

try:
    test_guilds = [int(os.getenv("TEST_GUILD"))]
finally:
    test_guilds = []

platforms = Literal["instagram", "twitter", "twitch", "youtube"]

log = logging.getLogger("Configuration cog")
coloredlogs.install(logger=log)
# TODO: Add error handler cog.
# NOTE: Check if channel is None before posting attempts.


class PlatformConfiguration(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.warn(f"{self.__class__.__name__} Cog has been loaded")

    @commands.slash_command(name="set-platform-channel", guild_ids=test_guilds)
    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set_platform_channel(
            self,
            inter: disnake.ApplicationCommandInteraction,
            platform_type: platforms,
            channel: disnake.TextChannel
    ) -> None:
        """Set announcement channel for any platform

        Parameters
        ----------
        platform_type: A social platform of choice.
        channel: Announcement channel for afore mentioned platform.
        """

        inter.response.defer
        cursor = await self.bot.conn.execute(
            f"SELECT {platform_type}_channel_id FROM data WHERE guild_id='{inter.guild.id}';"
        )
        data = await cursor.fetchall()
        await self.bot.conn.commit()
        await cursor.close()

        cursor = await self.bot.conn.execute(
            f"INSERT INTO data(guild_id,{platform_type}_channel_id) VALUES ({inter.guild.id},{channel.id});" if len(data) == 0 else
            f"UPDATE data SET {platform_type}_channel_id={channel.id} WHERE guild_id={inter.guild.id};"
        )
        await self.bot.conn.commit()
        await cursor.close()
        return await inter.response.send_message(
            content=f"{platform_type.capitalize()} announcement channel has been set to <#{channel.id}>.",
            ephemeral=True
        )

    @commands.slash_command(name="remove-platform-channel", guild_ids=test_guilds)
    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remove_platform_channel(
            self,
            inter: disnake.ApplicationCommandInteraction,
            platform_type: platforms
    ) -> None:
        """Remove announcement channel for any platform

        Parameters
        ----------
        platform_type: A social platform of choice.
        """

        inter.response.defer
        cursor = await self.bot.conn.execute(
            f"SELECT {platform_type}_channel_id FROM data WHERE guild_id='{inter.guild.id}';"
        )
        data = await cursor.fetchall()
        await self.bot.conn.commit()
        await cursor.close()

        if (not data) or data[0][0] is None:
            return await inter.response.send_message(
                content=f"{platform_type.capitalize()} has not been set yet. Nothing changed.",
                ephemeral=True,
            )
        else:
            cursor = await self.bot.conn.execute(
                f"UPDATE data SET {platform_type}_channel_id = NULL WHERE guild_id={inter.guild.id};"
            )
            await self.bot.conn.commit()
            await cursor.close()
            return await inter.response.send_message(
                content=f"{platform_type.capitalize()} channel record has been deleted",
                ephemeral=True,
            )

    @commands.slash_command(name="set-notification-role", guild_ids=test_guilds)
    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set_role(
            self,
            inter: disnake.ApplicationCommandInteraction,
            role: disnake.Role
    ) -> None:
        """Set the role to ping when any platform triggers a succesful post.

        Parameters
        ----------
        role: A role to ping when a post is created.
        """

        inter.response.defer
        cursor = await self.bot.conn.execute(
            f"SELECT notification_role_id FROM data WHERE guild_id='{inter.guild.id}';"
        )
        data = await cursor.fetchall()
        await self.bot.conn.commit()
        await cursor.close()

        cursor = await self.bot.conn.execute(
            f"INSERT INTO data(guild_id,notification_role_id) VALUES ({inter.guild.id},{role.id});" if len(data) == 0 else
            f"UPDATE data SET notification_role_id={role.id} WHERE guild_id={inter.guild.id};"
        )
        await self.bot.conn.commit()
        await cursor.close()
        return await inter.response.send_message(
            content=f"Notification mention role has been set to <@&{role.id}>",
            ephemeral=True
        )

    @commands.slash_command(name="remove-notification-role", guild_ids=test_guilds)
    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remove_notification_role(
            self,
            inter: disnake.ApplicationCommandInteraction,
    ) -> None:
        """Remove notification mentions.
        """

        inter.response.defer
        cursor = await self.bot.conn.execute(
            f"SELECT notification_role_id FROM data WHERE guild_id='{inter.guild.id}';"
        )
        data = await cursor.fetchall()
        await self.bot.conn.commit()
        await cursor.close()

        if (not data) or data[0][0] is None:
            return await inter.response.send_message(
                content="Notification mention role hasn't been setup yet. Nothing changed.",
                ephemeral=True,
            )
        else:
            cursor = await self.bot.conn.execute(
                f"UPDATE data SET notification_role_id = NULL WHERE guild_id={inter.guild.id};"
            )
            await self.bot.conn.commit()
            await cursor.close()
            return await inter.response.send_message(
                content="Notification mention role has been deleted.",
                ephemeral=True,
            )

    @commands.slash_command(name="view-server-configuration", guild_ids=test_guilds)
    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def view_server_configuration(
            self,
            inter: disnake.ApplicationCommandInteraction,
    ) -> None:
        """View server configuration.
        """

        inter.response.defer
        cursor = await self.bot.conn.execute(
            f"SELECT * FROM data WHERE guild_id='{inter.guild.id}';"
        )
        data = await cursor.fetchall()
        await self.bot.conn.commit()
        await cursor.close()

        class IDType(enum.Enum):
            Role = 0
            Channel = 1

        def parse_none(data: str | None, data_type: IDType, fallback_str: str = "Not set.") -> str:
            if data is None:
                return fallback_str
            else:
                match data_type:
                    case IDType.Channel:
                        return "<#" + str(data) + ">"
                    case IDType.Role:
                        return "<@&" + str(data) + ">"
                # If the idtype passed isn't one that we support, we return fallback string.
                return fallback_str

        data                 = data[0]  # noqa
        instagram_channel_id = parse_none(data[1], IDType.Channel)  # noqa
        twitch_channel_id    = parse_none(data[2], IDType.Channel)  # noqa
        twitter_channel_id   = parse_none(data[3], IDType.Channel)  # noqa
        youtube_channel_id   = parse_none(data[4], IDType.Channel)  # noqa
        notification_role_id = parse_none(data[5], IDType.Role)  # noqa

        return await inter.response.send_message(
            embed=disnake.Embed(
                title="Socials Bot",
                description="Server configuration",
                colour=inter.author.colour,
            ).set_author(
                name="Written by Shinyzenith#2939",
                url="https://shinyzenith.xyz/",
                icon_url="https://aakash.is-a.dev/images/avatar.png"
            ).add_field(
                name="Info:",
                value=f"Guild: {inter.guild.name}\nNotification Role: {notification_role_id}\n\nInstagram Channel: {instagram_channel_id}\nTwitch Channel: {twitch_channel_id}\nTwitter Channel: {twitter_channel_id}\nYouTube Channel: {youtube_channel_id}",  # noqa
                inline=True
            ),
            ephemeral=True
        )


def setup(bot: commands.Bot):
    bot.add_cog(PlatformConfiguration(bot))
