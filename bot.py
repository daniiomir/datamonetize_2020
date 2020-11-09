import re
import requests
import json
import time
from flask import Flask, request, jsonify


# start link - https://api.whatsapp.com/send?phone=74951896618&text=Start

login = "test"
passwd = "test"

url = "http://sds.smstraffic.ru/smartdelivery-in/multi.php"
url2 = "http://sds2.smstraffic.ru/smartdelivery-in/multi.php"

barcode = 'http://62.109.8.10/barcode.jpg'

greetings = """
Здравствуйте! Я чат-бот бонусной программы *[название компании]*.
Я умею быстро регистрировать бонусные карты и помогать вам учаcтвовать в наших квестах.\n
Чтобы быстро зарегистрировать бонусную карту, напишите - *Хочу карту*\n
Чтобы увидеть вашу карту, напишите - *Моя карта*\n
Чтобы участвовать в квесте, напишите - *Квест*
"""

promo = """
*1*. Квест "Супер акция Пятёрочки" - получи 500 баллов за покупку предложенных товаров в наших магазинах.

*2*. Квест "Бьюти" - получи от 1000 до 5000 баллов за покупку предложенных товаров красоты у наших партнеров.

Чтобы узнать подробнее про условия акции, напишите ее номер (*1* или *2*)
"""

promo_1 = """
Квест "Супер акция Пятерочки!"

Мы подобрали товары, которые могут вас максимально заинтересовать!

Набор "Футбольный болельщик":
1. Чипсы "Lay's" со сметаной и луком большая пачка
2. Безалкогольное пиво "Балтика" 0.5 л
3. Сухарики "Кириешки" с лососем и сыром

Набор "Семейный"
1. Подгузники "Huggies"
2. Молочная смесь "Питательная"
3. Презервативы "Гусарские"

Собери набор из предложенных товаров, получи бонусный промокод и выиграй *[название приза]*

"""

promo_2 = """
Квест "Бьюти"

Мы подобрали товары у наших партнеров, которые могут вас максимально заинтересовать!

Фен "Советский" в [название магазина] и получи 1000 баллов 
Косметичка "Max Factor" в [название магазина] и получи 2000 баллов
Лак для волос "FLEXTAPE" в [название магазина] и получи 3000 баллов

Купи любой из предложенных товаров, отправь нам промокод с чека и получи бонусы!

"""

promo_partners = """
В течении месяца совершите покупки у наших партнеров:

*[название магазина]* и получи 1000 руб
*[название магазина]* и получи 2000 руб
*[название магазина]* и получи 3000 руб

"""

how_to_promo = "Для получения бонусов необходимо ввести промокод, полученный при покупке товара, в формате *PROMO-XXXXXXX*\n"

phone_base = { # Телефон [ ФИО / EMAIL / Полная регистрация /  { промоакция : количество введенных промокодов } ]
				'79999718671':['Даниил Вячеславович Миронов', 'daniiomir@yandex.ru', 1, {'pepsi':1, 'absolut':5}],
			}

promocode_base = {
	"pepsi":['1', '11'],
	"absolut":['2', '22']
}

promocodes = ['12345', '11111']

wait_for_fio = []
wait_for_email = []
wait_for_agree = []

reg_fio = r'^[А-Я][а-я]+[\s]+[А-Я][а-я]+[\s]+[А-Я][а-я]+[\s]*$'
reg_email = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"

app = Flask(__name__)

def send_msg(phones, msg, rus):
	data = {
	"login":login,
	"password":passwd,
	"phones":phones,
	"message":msg,
	"rus":rus
	}
	x = requests.post(url, data=data)
	print(x.text)

def valid_promo(str):
	promo_str = str.split('-')
	if len(promo_str) == 1:
		return 3
	elif len(promo_str) == 2:
		if promo_str[0].lower() == 'promo' and promo_str[1] in promocodes:
			return 1
		elif promo_str[0].lower() == 'promo' and promo_str[1] not in promocodes:
			return 2
		else:
			return 3
	else:
		return 3

@app.route('/status', methods=['POST']) 
def status():
	# print(request.form.to_dict())
	return request.form

@app.route('/msg', methods=['POST']) 
def msg():
	data = request.json
	print(data)

	if data['text'] == 'Старт' or data['text'] == 'Start':
		send_msg(data['user_id'], greetings, 1)

##############################################################################################

	if data['text'] == "Квест":
		if data['user_id'] in phone_base:
			send_msg(data['user_id'], "У нас есть для вас персональные квесты с бонусами лично для вас!\n" + promo + "\nДля возврата в стартовое меню напишите *Начало*.", 1)
		else:
			send_msg(data['user_id'], "Для участия в квестах вам необходимо зарегистрироваться.\nНапишите ваше ФИО полностью. Пример - Иван Иванович Иванов.", 1)
			wait_for_fio.append(data['user_id'])

	if re.fullmatch(reg_fio, data['text']) != None and data['user_id'] in wait_for_fio:
		send_msg(data['user_id'], 'Спасибо. Теперь введите свой email', 1)
		phone_base[data['user_id']] = [data['text'], '', 0, {"pepsi":0, "absolut":0}]
		wait_for_fio.remove(data['user_id'])
		wait_for_email.append(data['user_id'])
	elif re.fullmatch(reg_fio, data['text']) == None and data['user_id'] in wait_for_fio and data['text'] != 'Квест':
		send_msg(data['user_id'], 'Введите ваше полное ФИО заново.', 1)

	if re.fullmatch(reg_email, data['text']) != None and data['user_id'] in wait_for_email:
		send_msg(data['user_id'], "Спасибо. Теперь нам необходимо ваше согласие на использование конфиденциальных данных.\nЧтобы подтвердить согласие - напишите *Согласен*", 1)
		phone_base[data['user_id']][1] = data['text']
		wait_for_agree.append(data['user_id'])
		wait_for_email.remove(data['user_id'])
	elif re.fullmatch(reg_email, data['text']) == None and data['user_id'] in wait_for_email and phone_base[data['user_id']][0] != data['text']:
		send_msg(data['user_id'], "Введите ваш email заново.", 1)

	if data['user_id'] in wait_for_agree and data['text'] == 'Согласен':
		send_msg(data['user_id'], "Спасибо. Вот ваш индивидуальный штрихкод от бонусной карты. При покупках не забывайте предъявлять его на кассе. " + barcode, 1)
		# send_msg(data['user_id'], barcode, 1)
		time.sleep(1)
		send_msg(data['user_id'], "У нас есть для вас персональные квесты с бонусами лично для вас!\n" + promo + "\nДля возврата в стартовое меню напишите *Начало*.", 1)
		phone_base[data['user_id']][1] = data['text']
		phone_base[data['user_id']][2] = 1
		wait_for_agree.remove(data['user_id'])
	elif data['user_id'] in wait_for_agree and phone_base[data['user_id']][1] != data['text']:
		send_msg(data['user_id'], "Нам необходимо ваше согласие на использование конфиденциальных данных.\nЧтобы подтвердить согласие - напишите *Согласен*", 1)

	if data['user_id'] in phone_base and (data['text'] == '1' or data['text'] == '2'):
		if phone_base[data['user_id']][2] == 1:
			if data['text'] == '1':
				send_msg(data['user_id'], promo_1 + how_to_promo, 1)
			elif data['text'] == '2':
				send_msg(data['user_id'], promo_2 + how_to_promo, 1)

#############################################################################################

	if data['user_id'] in phone_base and valid_promo(data['text']) == 1:
		send_msg(data['user_id'], "Поздравляем! Мы начислили вам N баллов.", 1)
	elif data['user_id'] in phone_base and valid_promo(data['text']) == 2:
		send_msg(data['user_id'], "Вы ввели неправильный промокод. Попробуйте еще раз.", 1)

#############################################################################################

	if data['text'] == 'Начало':
		send_msg(data['user_id'], greetings, 1)

#############################################################################################

	if data['text'] == 'Хочу карту' and data['user_id'] not in phone_base:
		send_msg(data['user_id'], "Здравствуйте! Напишите ваше ФИО полностью. Пример - Иван Иванович Иванов.", 1)
		wait_for_fio.append(data['user_id'])
	elif data['text'] == 'Хочу карту' and data['user_id'] in phone_base:
		send_msg(data['user_id'], "У вас уже есть наша бонусная карта. Чтобы увидеть ее, напишите - *Моя карта*", 1)
#############################################################################################

	if data['text'] == 'Моя карта':
		if data['user_id'] in phone_base:
			send_msg(data['user_id'], 'Просим любить и жаловать - ваша индивидуальная скидочная карта! ' + barcode, 1)
			# send_msg(data['user_id'], , 1)
		else:
			send_msg(data['user_id'], 'Для получения карты нужно зарегистироваться. Напишите *Хочу карту*', 1)

	return request.get_json(force=True)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=False)
