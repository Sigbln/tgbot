import menu

menu_message = 'Выберете ваш вариант'
ans_1 = 'Введите короткое имя нужной валюты. Например: BTC'
ans_2 = 'Введите день в формате DD.MM.YYYY'
error = 'Oops, smth went wrong, try /start again'
unsub_1 = "Вы итак не подписаны."
unsub_2 = "Вы успешно отписаны от рассылки."


def mess_gen(resp, coin=menu.btn_all):

    date = resp['date'].split('-')
    date = f'{date[2]}.{date[1]}.{date[0]}'
    message = f'*Курс на:* {date}\n'
    if coin == menu.btn_all:
        for i in resp['rates'].keys():
            message += f'\n*1 {resp["base"]}* = {resp["rates"][i]} {i}'
    elif coin in resp["rates"].keys():
        message += f'\n*1 {resp["base"]}* = {resp["rates"][coin]} {coin}'
    else:
        message = f'Извините, мы ничего не знаем о {coin}\n' \
                  f'Возможно вы ввели неправильное имя'
    return message
