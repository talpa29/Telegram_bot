import socketserver
import http.server
import ssl
import json
import requests



class bitcoin_Address:  # case sensitive. start with 1
    def __init__(self, addr):
        self.addr = addr

    def getAdd(self):
        return self.addr


class Legacy(bitcoin_Address):  # case sensitive. start with 1
    def isLegacy(self):
        return True


class Nested_SegWit(bitcoin_Address):  # case sensitive start with 3
    def isNested_segwit(self):
        return True


class Native_SegWit(bitcoin_Address):  # no case sensitive start with bc1
    def isNative_segwit(self):
        return True

website = "https://www.blockchain.com/btc/address/"


def getResponse(user_input):
    address = str(user_input).split()
    if len(address) > 20:
        return "input length too long"
    else:
        balances = ""
        for s in address:
            if s[0] == '1' and len(s) > 30:
                legacy = Legacy(s)
                site = website + legacy.getAdd()
                balance = getBalance(site)
                balances = balances + s + " balance is: " + balance + "\n"
            elif s[0] == '3' and len(s) > 30:
                nested = Nested_SegWit(s)
                site = website + nested.getAdd()
                print(site)
                balance = getBalance(site)
                balances = balances + s + " balance is: " + balance + "\n"
            elif s[0] == 'b' and s[1] == 'c' and s[2] == '1' and len(s) > 30:
                native = Native_SegWit(s)
                site = website + native.getAdd()
                balance = getBalance(site)
                balances = balances + s + " balance is: " + balance + "\n"
            else:
                balances = balances + s + " is not a valid bitcoin address" + "\n"
    return balances


def getBalance(site):
    s = requests.get(site)
    balance_index = s.text.find("Final Balance")
    balance = s.text[balance_index:balance_index + 200]
    balance_index = balance.find("BTC")
    balance = balance[balance_index - 11:balance_index]
    if balance == "":
        return "not a valid bitcoin address"
    else:
        return balance

def getqrResponse(user_input):
    API_URL = 'http://api.qrserver.com/v1/read-qr-code/'
    response = requests.post(url=API_URL, files={'file': user_input})
    json_response = json.loads(response.content)
    address_index = str(json_response).find("data")
    address = str(json_response)[address_index:len(str(json_response))].split()[1]
    address = address[1:len(address) - 2]
    return getResponse(address)

class myHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        json_data = json.loads(post_data)  # json that contains data that sent from telegram api

        index = str(json_data).find("photo")
        if index != -1:
            chat_id = json_data['message']['from']['id']
            user_input = json_data['message']['photo']
            file_id_index = str(user_input).find("file_id")
            file_id = str(user_input)[file_id_index:len(str(user_input))].split()[1]
            file_id = file_id[1:len(file_id) - 2]
            get_file_api_url = f'https://api.telegram.org/bot5429058565:AAH4D6srwFqB7BIwTmEYdVPKelVQtWURKK0/getFile'
            get_file_content_api_url = f'https://api.telegram.org/file/bot5429058565:AAH4D6srwFqB7BIwTmEYdVPKelVQtWURKK0/' + '/{file_path}'
            response = requests.post(url=get_file_api_url, params={'file_id': file_id})
            json_response = json.loads(response.content)
            response = requests.get(url=get_file_content_api_url.format(file_path=json_response['result']['file_path']))
            user_input = json_response
            bot_output = getqrResponse(response.content)
        else:
            chat_id = json_data['message']['from']['id']
            user_input = json_data['message']['text']
            bot_output = getResponse(user_input)


        url = "https://api.telegram.org/bot5429058565:AAH4D6srwFqB7BIwTmEYdVPKelVQtWURKK0/sendMessage"

        req = requests.post(url=url,
                            params={'chat_id': chat_id, 'text': bot_output})  # send request to the api of the telegram
        if req.status_code == 200:
            self.send_response(200)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()



server = socketserver.TCPServer(('0.0.0.0', 8443), myHandler)
server.socket = ssl.wrap_socket(server.socket,
                                ca_certs="SSL/ca_bundle.crt",
                                certfile="SSL/certificate.crt",
                                keyfile="SSL/private.key",
                                server_side=True
                                )

server.serve_forever()