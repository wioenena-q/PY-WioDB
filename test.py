from wiodb import MongoProvider
from wiodb import JsonProvider
from wiodb import SqliteProvider
from wiodb.src.Base import Base
from wiodb.src.Util import Util
import random
import json
import pydash


with open("config.json", "r") as file:
    data = json.loads(file.read())

    url = data["url"]


