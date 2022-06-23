import logging
import os
from typing import Literal

import coloredlogs
import disnake
from disnake.ext import commands

test_guilds = [int(os.getenv("TEST_GUILD"))]

log = logging.getLogger("Configuration cog")
coloredlogs.install(logger=log)
# TODO: Add error handler cog.
# TODO: Add slash command to check current server configuration.
# TODO: Add slash command to REMOVE platform channel ids.
# NOTE: Note ^ Check if channel is None before removal / posting attempts.


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
            platform_type: Literal[
                "instagram",
                "twitter",
                "twitch",
                "youtube"
            ],
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


def setup(bot: commands.Bot):
    bot.add_cog(PlatformConfiguration(bot))
