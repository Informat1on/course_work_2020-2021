import json
from classes.bot_class import FindBookBot

try:
    config = json.load(open('config.json'))
    bot_token = config['bot_token']

    # создаем экземпляр класса
    bot = FindBookBot(bot_token)
    # запускаем бота>
    bot.start()

# если не найден файл коонфига
except FileNotFoundError:
    print("FATAL ERROR: Could not find config file")

# когда файл json не валидный
except json.decoder.JSONDecodeError:
    print("FATAL ERROR: Could not read config file, invalid JSON")

# если не знаем ошибку
except Exception as e:
    print("Unknown error: " + str(e))