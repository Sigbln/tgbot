import requests
import shelve

import config


class DataBase:
    """Для взаимодействия с БД"""

    def __init__(self):
        self.resp = None
        self.sub_base = 'data/sub.db'
        self.data_base = 'data/data.db'
        self.ans_1 = 'Вы успешно подписаны'
        self.ans_2 = 'Вы и так уже подписаны'
        self.ans_3 = 'Вы успешно отписались'
        self.ans_4 = 'Вы и так не подписаны'

    def get_subs(self):

        """Получаем список tgID всех подписчиков"""

        temp = []
        with shelve.open(self.sub_base) as followers:
            for user in followers:
                if followers[user]:
                    temp.append(user)
            return temp

    def add_sub(self, temp_id):

        """Если пользователь ещё не подписан/не активная подписка, то добавляем
        его или обновляем подписку"""

        with shelve.open(self.sub_base) as followers:
            if temp_id not in followers or not followers[temp_id]:
                followers[temp_id] = True
                return self.ans_1
            else:
                return self.ans_2

    def unsub(self, temp_id):

        """Если пользователь не подписан/имеет активную подписку, то запоминаем
        его/ставим не актив"""

        with shelve.open(self.sub_base) as followers:
            if temp_id not in followers.keys() or followers[temp_id]:
                followers[temp_id] = False
                return self.ans_3
            else:
                return self.ans_4

    def update_data(self, date=None):

        """Вызывается только в том случае, если в БД нет информации за данный
        день. Делает get запрос и заносит результат в БД, после чего возвращает
        его"""

        if date is None:
            self.resp = requests.get(config.url_latest).json()
        else:
            self.resp = requests.get(
                config.url_date_first + date + config.url_date_last).json()
            with shelve.open(self.data_base) as data:
                date = self.resp['date']
                data[date] = self.resp
                return data[date]

    def get_rates(self, date):

        """Смотрит есть ли информация в БД за данный денью Возвращает его если
        есть, обновляет если нет"""

        with shelve.open(self.data_base) as data:
            if date in data:
                return data[date]
            else:
                return self.update_data(date)
