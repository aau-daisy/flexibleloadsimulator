import yaml
from attrdict import AttrDict
import os

stream = file(os.getcwd() + '/' + 'resources/app.yaml', 'r')
params = AttrDict(yaml.safe_load(stream))

# A storage engine to save revoked tokens. In production if
# speed is the primary concern, redis is a good bet. If data
# persistence is more important for you, postgres is another
# great option. In this example, we will be using an in memory
# store, just to show you how this might work. For more
# complete examples, check out these:
# https://github.com/vimalloc/flask-jwt-extended/blob/master/examples/redis_blacklist.py
# https://github.com/vimalloc/flask-jwt-extended/tree/master/examples/database_blacklist
blacklist = set()

