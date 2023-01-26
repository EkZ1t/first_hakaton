import requests
import telebot
from telebot import types 
from bs4 import BeautifulSoup 
from bs4.element import ResultSet, Tag


URL = 'https://kaktus.media/?lable=8&date=2023-01-26&order=time'

# основной парсинг

def get_html(url: str):
    html = requests.get(url)
    return html.text

def get_cards(html: str):
    soup = BeautifulSoup(html, 'lxml')
    cards = soup.find_all('div', class_='Tag--article')
    return cards

def cards_parser(cards: ResultSet): 
    result = []
    for card in cards:
        title = card.find('a', class_='ArticleItem--name').text
        link = card.find('a', class_='ArticleItem--name').get('href')
        try:
            image_link = card.find('img', class_ ='ArticleItem--image-img lazyload').get('src')
        except AttributeError:
            image_link = 'картинки нет'
            
        obj = {
            'title': title,
            'link': link, 
            'image_link': image_link 
        }
        
        result.append(obj)
    return result


def get_data_for_bot() -> list:
    html = get_html(URL)
    cards = get_cards(html)
    list_of_data = cards_parser(cards)
    return list_of_data
   
# парсинг ссылки на статью
def get_article(article_number: int):
    data = get_data_for_bot()
    url = data[article_number]['link']
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml')
    article = soup.find('div', class_='BbCode').text.split()
    str_article = ''
    for i in article:
        if i.endswith('.'):
            str_article += ' '
            str_article += i
            str_article += ' '
        else:
            str_article += ' '
            str_article += i
            
    return str_article
    
    
# дальше прописан бот 

token = '5989491257:AAETv6BlKl68IzHt4GaNOYxYacOtcvf93ro'
bot = telebot.TeleBot(token)
    
    
@bot.message_handler(commands=['start', 'hi'])
def first_message(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('news')
    keyboard.add(button)
    bot.send_message(message.chat.id, 'нажми на news чтобы получить список новостей', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'news')
def keyboard_starter(message: types.Message):
    data = get_data_for_bot()
    inline_keyboard = types.InlineKeyboardMarkup()
    for i in range(20):
        name = data[i]['title']
        button = types.InlineKeyboardButton(f'{name}', callback_data=f'{i}')
        inline_keyboard.add(button)
    bot.send_message(message.chat.id, 'вот список последних новостей', reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda callback: callback.data == 'quit')
def end_task(callback: types.CallbackQuery):
    bot.send_message(callback.message.chat.id, 'До свидания')


@bot.callback_query_handler(func=lambda callback: int(callback.data) in range(20))
def send_preview(callback: types.CallbackQuery):
    data = get_data_for_bot()
    article = get_article(int(callback.data))
    link_number = int(callback.data)
    
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_buttton = types.InlineKeyboardButton('quit', callback_data='quit')
    inline_keyboard.add(inline_buttton)
    
    bot.send_message(callback.message.chat.id, f'Держи статью! \n {data[int(callback.data)]["title"]} {data[int(callback.data)]["image_link"]} \n \n {article}', reply_markup=inline_keyboard)

bot.polling()