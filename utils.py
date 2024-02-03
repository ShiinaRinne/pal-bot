import yaml
import psutil
from psutil._common import bytes2human
from typing import Dict

from khl import Message


def read_config():
    with open('config.yml', 'r') as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)

config:Dict = read_config()
prefixes = config["prefixes"]

def test_rules(msg: Message):
    return 'test' in msg.content

def check_admin(author_id: str):
    return author_id in config["admin"] or config["admin"] == []

def check_if_mention(text: str):
    return text.startswith("(met)") and text.endswith("(met)")

def dump_mention_to_id(text: str):
    return text.replace("(met)","")




cpu_percent = psutil.cpu_percent(interval=1)  # 1秒内的平均CPU占用率
memory_info = psutil.virtual_memory()


