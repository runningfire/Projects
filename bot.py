import logging
import ephem  
from datetime import datetime                    
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


def main():
    updater = Updater('408378429:AAFD2PRwO9Breirqf5FZyLZVvNhtVc25m0U')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("planet",constel ))
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    updater.start_polling()
    updater.idle()


def talk_to_me(bot, update):
    user_text = update.message.text 
    print(user_text)
    update.message.reply_text(user_text)   


def greet_user(bot, update):
    text = 'Работаю'
    print(text) 
    update.message.reply_text(text)


# /planet
# Mercury

# /planet Mercury

def constel(bot, update):
    update.message.reply_text('Привет,данная команда находит в каком созвездии находится сегодня та или иная планета.Введи название планеты на английском языке и узнаешь.')
    user_text1 = update.message.text
    print(user_text1)
    today = str(datetime.now())
    dt = today.split(' ')
    print(dt)
    split_text = user_text1.split(' ')
    flag = False
    if split_text[1] == 'Mercury':
        local = ephem.Mercury()
        flag = True
    elif split_text[1] == 'Venus':
        local = ephem.Venus()
        flag = True
    elif split_text[1] == 'Earth':
        local = ephem.Earth()
        flag = True
    elif (split_text[1] == 'Mars'):
        local = ephem.Mars()
        flag = True

    if flag == True: 
        local.compute(dt[0])
        cons = ephem.constellation(local)
        print(cons)
        update.message.reply_text(cons)    
    else:
        text = 'Неверный ввод'
        print(text)
        update.message.reply_text(text)          
 
if __name__ == '__main__':
    main()
