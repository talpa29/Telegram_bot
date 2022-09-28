from aiogram import Bot, Dispatcher, executor, types
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
site = "https://bitref.com/"

class Legacy:#case sensitive. start with 1
    def __init__(self, addr):
        self.addr = addr

    def getAd(self):
        return self.addr


class Nested_SegWit:#case sensitive start with 3
    def __init__(self, addr):
        self.addr = addr

    def getAd(self):
        return self.addr


class Native_SegWit:#no case sensitive start with bc1
    def __init__(self, addr):
        self.addr = addr

    def getAd(self):
        return self.addr


bot = Bot(token='5627331950:AAHzGbPITEp3rCBdGP4kPDlNRmpFnFlHaUU')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    await message.reply("hello!, my name is tal bot")


@dp.message_handler()
async def getBitcoinBalance(message: types.Message):
    address = message.text.split()
    for s in address:
        if s[0] == '1' and len(s) > 30:
            legacy = Legacy(s)
            web = site + legacy.getAd()
            await getBalance(s,web,message)
        elif s[0] == '3' and len(s) > 30:
            nested = Nested_SegWit(s)
            web = site + nested.getAd()
            await getBalance(s,web,message)
        elif s[0] == 'b' and s[1] =='c' and s[2] == '1' and len(s) > 30:
            native = Native_SegWit(s)
            web = site + native.getAd()
            await getBalance(s,web,message)
        else:
            await message.answer(s + " is not a valid bitcoin address")


async def getBalance(s,web,message):
    driver.get(web)
    time.sleep(3)
    search = driver.find_element("id", "final_balance")
    balance = search.text
    if balance[0] == 'l':
        await message.answer(s + " is not a valid bitcoin address")
    else:
        await message.answer(s + " balance is: " + balance)

executor.start_polling(dp)