from .models import MasterConfig


class MasterConfigManager:
    @staticmethod
    def get_config(key: str, default=None):
        try:
            return MasterConfig.objects.get(key=key).value
        except MasterConfig.DoesNotExist:
            return default

    @staticmethod
    def get_config_value(key: str, subkey: str, default=None):
        config = MasterConfigManager.get_config(key, {})
        return config.get(subkey, default)
