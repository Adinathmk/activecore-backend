import os

env = os.getenv("DJANGO_ENV", "development")

if env == "production":
    from .prod import *
else:
    from .dev import *
