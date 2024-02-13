import json


# 读取配置
def load_config():
    with open("./config/configs.json", "r") as file:
        config = json.load(file)
    return config


# 更新配置
def update_config(key, value):
    config = load_config()
    config[key] = value
    with open("./config/configs.json", "w") as file:
        json.dump(config, file, indent=4)
