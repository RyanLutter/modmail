import os
import json
import box


class ConfigManager:
    """Class that manages a cached configuration"""

    valid_keys = {
        'prefix', 'status', 'guild_id',
        'mention', 'disable_autoupdates',
        'modmail_guild_id', 'token', 'snippets',
        'aliases', 'owners', 'modmail_api_token'
    }

    allowed_to_change_in_command = valid_keys - {'token', 'snippets', 'aliases', 'owners', 'modmail_api_token'}

    def __init__(self, bot):
        self.bot = bot
        self.cache = box.Box()
        self._modified = True
        self.populate_cache()

    @property
    def api(self):
        return self.bot.modmail_api

    def populate_cache(self):
        try:
            data = json.load(open('config.json'))
        except FileNotFoundError:
            data = {}
        finally:
            data.update(os.environ)
            data = {k.lower(): v for k, v in data.items() if k.lower() in self.valid_keys}
            self.cache = data

        self.bot.loop.create_task(self.refresh())

    async def update(self, data=None):
        """Updates the config with data from the cache"""
        self._modified = False
        if data is not None:
            self.cache.update(data)
        await self.api.update_config(self.cache)

    async def refresh(self):
        """Refreshes internal cache with data from database"""
        data = await self.api.get_config()
        self.cache.update(data)

    def __getattr__(self, value):
        return self.cache[value]

    def __setitem__(self, key, item):
        self.cache[key] = item

    def __getitem__(self, key):
        return self.cache[key]

    def get(self, value, default=None):
        return self.cache.get(value) or default
