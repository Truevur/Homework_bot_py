from urllib.parse import urlencode, quote_plus
import urllib3
import time
import json
from messages import messages, not_valid_method
import os.path

http = urllib3.PoolManager()
API = 'https://api.telegram.org/bot'
TOKEN = '1944178112:AAEN_vu-VeqRtNxf-7MWasMY5sOfYSw_aJU'
URL = API + TOKEN
INVALID_UPDATE_ID = -1
HELP_FOR_BREADS = """
You find a secret help (for users)!!!
/help - Help
/adduser - your login and passwd in VK format: /adduser <login> <password>
/listuser - show list of your VK accounts
/listchats - get list of chat id in normal order, format: /listchats username (you can set number of chats in second parameter)
/sendmessage - send message to VK chat format: /sendmessage <login> <chatid> <text>
/sendmessagetime - send message to VK after time (UTC) format: /sendmessage <login> <chatid> <time> <text>
/time - show current server time in correct format (UTC)
"""
EMPTY_MESSAGES = """{
  "users":{},
  "messages":[]
}"""


def getUpdates(offset=-10):
    get = URL + '/getUpdates?offset=' + str(offset)
    response = http.request('GET', get)
    res = response.data
    return res


def getCommand(lid, mes):
    js = json.loads(getUpdates())
    for message in js['result']:
        try:
            if message['update_id'] > lid:
                lid = message['update_id']
                f = open('.id.txt', 'w')
                f.write(str(lid))
                f.close()
                parse_message(message, mes)
        except BaseException:
            print('ERROR in message')
            print(message)
    return lid


def parse_message(message, mes):
    chatid = message['message']['chat']['id']
    text = message['message']['text']
    uid = str(message['message']['from']['id'])
    print(chatid, text)
    if text[0] == '/':
        command = text.split()
        if command[0] == '/help':
            print('help......')
            sendMessage(chatid, 'Only hardcode, no help')
        if command[0] == '/adduser':
            if len(command) == 3:
                mes['users'][uid] = mes['users'].get(uid, {})
                mes['users'][uid][command[1]] = command[2]
                sendMessage(chatid, 'Add new log and pass correct')
            else:
                sendMessage(chatid, 'Wrong number of attributes')
        if command[0] == '/listuser':
            sendMessage(chatid, getUsersList(mes, uid))
        if command[0] == '/listchats':
            if len(command) == 1:
                sendMessage(chatid, 'Give user alias from:\n' +
                            getUsersList(mes, uid))
            elif len(command) == 2:
                if mes['users'][uid].get(command[1]) is not None:
                    sendMessage(chatid, getVKMessageList(
                        command[1], mes['users'][uid][command[1]]))
                else:
                    sendMessage(chatid, 'Wrong user alias')
            elif len(command) == 3:
                if mes['users'][uid].get(command[1]) is not None:
                    sendMessage(chatid, getVKMessageList(
                        command[1], mes['users'][uid][command[1]], int(command[2])))
                else:
                    sendMessage(chatid, 'Wrong user alias')
            else:
                sendMessage(chatid, 'Wrong number of arguments')
        if command[0] == '/sendmessage':
            if len(command) <= 3:
                sendMessage(chatid, 'Wrong number of arguments')
            elif len(command) >= 4:
                sendMessageVK(command[1], mes['users'][uid][command[1]],
                              command[2], ' '.join(command[3:]))
        if command[0] == '/sendmessagetime':
            if len(command) <= 4:
                sendMessage(chatid, 'Wrong number of arguments')
            elif len(command) >= 5:
                try:
                    sendtime = time.strptime(command[3], '%Y.%m.%d-%H:%M:%S')
                    mes['messages'].append({
                        'chatid': chatid,
                        'log': command[1],
                        'pass': mes['users'][uid][command[1]],
                        'peerid': command[2],
                        'time': time.strftime('%Y.%m.%d-%H:%M:%S', sendtime),
                        'text': ' '.join(command[4:])
                    })
                    sendMessage(chatid, 'Message sheduled to ' +
                                time.strftime('%Y.%m.%d-%H:%M:%S', sendtime))
                except ValueError:
                    sendMessage(
                        chatid,
                        'Incorrect time format, please' +
                        ' use format like this:\n' +
                        time.strftime(
                            '%Y.%m.%d-%H:%M:%S',
                            time.gmtime()))
        if command[0] == '/time':
            sendMessage(chatid, time.strftime(
                '%Y.%m.%d-%H:%M:%S', time.gmtime()))
    if text == 'I need help!!!':
        sendMessage(chatid, HELP_FOR_BREADS)


def getUsersList(mes, uid):
    usrlist = ''
    if mes['users'].get(uid, None) is None:
        return 'You don`t add any users'
    for alias, token in mes['users'][uid].items():
        usrlist += alias + ': ' + token + '\n'
    return usrlist


def getVKMessageList(log, passwd, num=30):
    session = messages(log, passwd)
    try:
        response = session.method("messages.getConversations", count=num)
    except not_valid_method:
        return getVKMessageList(log, passwd)
    response = json.loads(response['payload'][1][0])
    res = ''
    for i in response['response']['items']:
        res += str(i['conversation']['peer']['id']) + ': ' + \
            i['last_message']['text'][:45] + '\n'
    return res


def sendMessageVK(log, passwd, peerid, text):
    session = messages(log, passwd)
    try:
        response = session.method(
            "messages.send", peer_id=peerid, message=text)
    except not_valid_method:
        sendMessageVK(log, passwd, peerid, text)


def sendMessage(chat_id, text):
    sendMessage = {
        'chat_id': chat_id,
        'text': text
    }
    get = URL + '/sendMessage?' + urlencode(sendMessage, quote_via=quote_plus)
    response = http.request('GET', get)


def strjson(data):
    return json.dumps(data, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    if not os.path.exists('.id.txt'):
        f = open('.id.txt', 'w')
        f.write('-1')
        f.close()
    if not os.path.exists('.messages.json'):
        f = open('.messages.json', 'w')
        f.write(EMPTY_MESSAGES)
        f.close()
    f = open('.id.txt')
    lid = int(f.read())
    f.close()
    fj = open('.messages.json')
    mes = json.load(fj)
    fj.close()
    try:
        iter = 0
        while True:
            try:
                lid = getCommand(lid, mes)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            newmessages = []
            for i in mes['messages']:
                if (time.mktime(time.strptime(i['time'], '%Y.%m.%d-%H:%M:%S')) <=
                        time.mktime(time.gmtime())):
                    sendMessageVK(i['log'], i['pass'], i['peerid'], i['text'])
                    sendMessage(i['chatid'], 'Sheduled message was sended')
                else:
                    newmessages.append(i)
            mes['messages'] = newmessages
            if iter >= 3600:
                fj = open('.messages_rec.json', 'w')
                json.dump(mes, fj, ensure_ascii=False, indent=4)
                fj.close()
            iter += 1
    except KeyboardInterrupt:
        fj = open('.messages.json', 'w')
        json.dump(mes, fj, ensure_ascii=False, indent=4)
        fj.close()
