# Libraries
from bs4 import BeautifulSoup
import requests
import telebot
import logging
import time
from telebot.storage import StateMemoryStorage
from telebot import custom_filters

# Files
import Description as Des
import Config as Keys
import Responses as Res


# Configure the logger
logging.basicConfig(
    level=logging.INFO,                                             
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
    handlers=[
        logging.FileHandler("bot.log"),                             
        logging.StreamHandler()                                     
    ]
)


# Create a bot object
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(Keys.API_KEY, state_storage=state_storage)
logging.info('Start bot...')


# start command
@bot.message_handler(commands=['start'])
def start_command(user_message):
    key_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    key_markup.add(telebot.types.KeyboardButton("🔎 سرچ 🔍"))

    bot.send_message(chat_id=user_message.chat.id, text=Des.start_description, reply_markup=key_markup)


# search
@bot.message_handler(func=lambda message: message.text == "🔎 سرچ 🔍")
def search(user_message):
    bot.send_message(chat_id=user_message.chat.id , text="🔍 نام محصول مورد نظرتان را بنویسید 🔻")
    bot.register_next_step_handler(user_message, scraping_data)


# scraping
def scraping_data(user_message):
    # dynamic url
    search_term = user_message.text
    search_term = search_term.replace(" ", "%20")
    url = f"https://torob.com/search/?query={search_term}&available=true" # {page}{stock_status}{available}{sort}
    response = requests.get(url)

    # respond, should be 200
    logging.info(response)

    if response.status_code == 200:
        # get the html text
        soup = BeautifulSoup(response.text, "html.parser")
        names = soup.find_all("h2", class_="ProductCard_desktop_product-name__JwqeK")

        # save the found items name, price, and link into dictionary
        items_found = {} 
        for name in names[:10]:  # Limit to the first 10 items
            # find the parents name
            parent = name.parent

            # find direct link from parent of parent
            link = parent.parent.get('href', '')

            # find the price from the parent
            price_tag = parent.find("div", class_="ProductCard_desktop_product-price-text__y20OV").string.split(" ")

            if len(price_tag) == 2:     # 100 تومان
                price = price_tag[0]
            elif len(price_tag) == 3:   # از 100 تومان
                price = price_tag[1]
            else:                       # 0
                price = "0"
            
            # save name, price, and link in a dictionary
            items_found[name.string] = {
                'price': int(price.replace("٫", "")),
                'link': link
            }

        # Format the items_found dictionary into a readable string with links
        message = "\n".join([f"{index + 1}. نام: <a href='https://torob.com{item['link']}'>{name}</a>\nقیمت: {item['price']} تومان💵\n\n" for index, (name, item) in enumerate(items_found.items())])

        # Send the message with HTML parsing enabled
        bot.send_message(chat_id=user_message.chat.id, text=message, parse_mode='HTML')
    else:
        bot.reply_to(user_message, "Error in fetching data!")


# Message response
@bot.message_handler()
def message_response(user_message):
    response = Res.sample_responses(user_message)
    bot.send_message(user_message.chat.id, response)


if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))

    logging.info('start pulling...')
    retry_delay = 5  # Initial delay in seconds

    while True:
        try:
            bot.polling()
        except requests.exceptions.ProxyError as e:
            logging.error(f"Proxy error: {e}")
            logging.info(f'Retrying in {retry_delay} seconds...')
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 300)  # Exponential backoff with a maximum delay of 5 minutes
        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception: {e}")
            logging.info(f'Retrying in {retry_delay} seconds...')
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 300)  # Exponential backoff with a maximum delay of 5 minutes
        else:
            retry_delay = 5  # Reset delay after a successful polling
    logging.info('end pulling...')