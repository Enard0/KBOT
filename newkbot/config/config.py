from abc import ABC
from typing import Final


class BotConfig(ABC):
    CMD_PREFIX: Final = '/'
    TOKEN: Final = 'ODA0NzE1MjgwMzYxNTg2NzQ4.YBQXgQ.Lt31etyrnf8FMLJOFPCLUaWUqAk'

class MusicConfig(ABC):
    HOST: Final="127.0.0.1"
    PORT: Final=3333
    LABEL: Final="MAIN"
    PASSWORD: Final="VYTIftiyFIYVtvgbTVGHtyvguHRDTKF7itukhgYg"