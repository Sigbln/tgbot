import unittest

from messages import mess_gen


class TestMess_gen(unittest.TestCase):

    def setUp(self):
        self.test_resp = {'base': 'EUR', 'date': '2021-02-14',
                          'rates': {'BTC': 1, 'RUB': 2, 'BYN': 3}}
        self.ans_all = f'*Курс на:* 14.02.2021\n' \
                       f'\n*1 EUR* = 1 BTC' \
                       f'\n*1 EUR* = 2 RUB' \
                       f'\n*1 EUR* = 3 BYN'
        self.ans_byn = f'*Курс на:* 14.02.2021\n' \
                       f'\n*1 EUR* = 3 BYN'
        self.ans_no_wallet = f'Извините, мы ничего не знаем о BRU\n' \
                             f'Возможно вы ввели неправильное имя'
        self.coin = 'RUB'
        self.test_func = mess_gen

    def test_all(self):
        self.assertEqual(self.test_func(self.test_resp), self.ans_all)

    def test_byn(self):
        self.assertEqual(self.test_func(self.test_resp, 'BYN'), self.ans_byn)

    def test_no_wallet(self):
        self.assertEqual(self.test_func(self.test_resp, 'BRU'),
                         self.ans_no_wallet)


if __name__ == "__main__":
    unittest.main()
