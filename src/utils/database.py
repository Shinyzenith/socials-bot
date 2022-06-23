import aiosqlite


class SqliteSingleton:
    __connection__ = None

    async def get_connection():
        if SqliteSingleton.__connection__ is None:
            SqliteSingleton.__connection__ = await aiosqlite.connect('data.db')
            cursor = await SqliteSingleton.__connection__.execute("""
                                            CREATE TABLE IF NOT EXISTS data(
                                                guild_id INTEGER PRIMARY KEY,
                                                instagram_channel_id INTEGER,
                                                twitch_channel_id INTEGER,
                                                twitter_channel_id INTEGER,
                                                youtube_channel_id INTEGER,
                                                notification_role_id INTEGER
                                            )
                                        """)
            await SqliteSingleton.__connection__.commit()
            await cursor.close()
        return SqliteSingleton.__connection__

    async def close_connection():
        await SqliteSingleton.__connection__.close()
        SqliteSingleton.__connection__ = None
