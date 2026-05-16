from .production import *  # noqa: F403,F401

# Staging peut activer DEBUG ponctuellement via variable
DEBUG = env.bool("DEBUG", default=False)
