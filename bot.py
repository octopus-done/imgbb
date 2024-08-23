import telebot
from pymongo import MongoClient
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve the environment variables
TOKEN = os.getenv('TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client['telegram_bot']
collection = db['users']

# Command to start the bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a photo and I'll upload it to IMGBB.")

# Handling photo messages
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
    
    # Upload to IMGBB
    imgbb_url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    response = requests.post(imgbb_url, data={'image': file_url})
    
    if response.status_code == 200:
        imgbb_response = response.json()
        imgbb_link = imgbb_response['data']['url']
        
        # Save the link and user info to MongoDB
        user_data = {
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'imgbb_link': imgbb_link
        }
        collection.insert_one(user_data)
        
        bot.reply_to(message, f"Photo uploaded successfully: {imgbb_link}")
    else:
        bot.reply_to(message, "Failed to upload the photo.")

# Running the bot
bot.polling()
