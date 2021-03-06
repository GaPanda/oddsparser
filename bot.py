# -*- coding: utf-8 -*-

# Украл заготовку отсюда: https://groosha.gitbooks.io/telegram-bot-lessons/content/chapter4.html

import telebot
import cherrypy
import config
import process

WEBHOOK_HOST = config.ip_address
WEBHOOK_PORT = config.port
WEBHOOK_LISTEN = config.listen_ip_address

WEBHOOK_SSL_CERT = config.cert_path
WEBHOOK_SSL_PRIV = config.key_path

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

#  Наш вебхук-сервер
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
            'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.send_message(message.chat.id, "Привет. Для начала введи команду /message.")


@bot.message_handler(commands=["match"])
def cmd_match(message):
    bot.send_message(message.chat.id,
                     "Отправь мне ссылку на матч с oddsportal, желательно баскетбол).\
                     \nПока что-это тест. Тут будет дефолтный матч.")
    match_url = 'http://www.oddsportal.com/basketball/brazil/nbb/paulistano-bauru-fsrT2vBe/'
    number = 5
    percents = 50
    try:
        bot.send_message(message.chat.id, "Количество матчей из истории: {}. \n \
                         Процент коэффициентов: {}".format(number, percents))

        node = process.Process(number, percents, match_url)
        node.run()
        bot.send_message(message.chat.id, "{} - {}".format(node.match.team_home, node.match.team_guest))
    except:
        bot.send_message(message.chat.id, "Ошибочка :(")


@bot.message_handler(commands=["close"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Пока.")


def main():
    # Снимаем вебхук перед повторной установкой (избавляет от некоторых проблем)
    bot.remove_webhook()

    #  Ставим заново вебхук
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    #  Указываем настройки сервера CherryPy
    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
    })

    #  Собственно, запуск!
    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
