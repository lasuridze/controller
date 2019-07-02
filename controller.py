import json
import os
import time
import traceback
from datetime import datetime
from threading import Thread
from multiprocessing import Process

import requests
import tornado.ioloop
import tornado.web

from read import listen_card, ELEVATORS  #amit xdeba read.py funqciebis shemotana
from controller_bt import bt_listener

TOKEN = 'krmkdfj89wh4ubfw94kwb4wubv4wtinw4u'
MAIN_SITE = 'https://pirosmani18.com'
STORE_KEY = 'ho_keys'
STORE_ALL_KEYS = 'ho_all_keys'
HISTORY_STORE_KEY = 'ho_access_history'

class Store:
    STORE_FILE = '/home/toka/c_store'

    def __init__(self):
        os.system('touch %s' % self.STORE_FILE)

    def set(self, key, value):
        s = json.loads(open(self.STORE_FILE, 'r').read() or '{}')
        s[key] = value
        with open(self.STORE_FILE, 'w') as f:
            f.write(json.dumps(s))

    def get(self, key, default=None):
        s = json.loads(open(self.STORE_FILE, 'r').read() or '{}')
        return s.get(key, default)

store = Store()

def address_updater():
    """
    Task to update controller's address on the main site.
    We're reading the host given by ngrok via its API
    """
    time.sleep(10)  # initial sleep while ngrok is starting up
    #os.system('/usr/bin/tunnel.sh')
    return
    while True:
        try:
            ngrok_resp = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
            ngrok_resp = ngrok_resp.json()
            address = ngrok_resp['tunnels'][0]['public_url']

            # Make POST request to main site API
            requests.post('{}/api/update_address'.format(MAIN_SITE), params={'token': TOKEN}, data=json.dumps({'address': address, 'elevators': ELEVATORS}))
        except:
            print "Address updater exception:"
            traceback.print_exc()

        time.sleep(90)


def update_keys():
    """
    Get list of keys from the main site and update locally stored list
    """
    try:
        resp = requests.get('{}/api/get_keys'.format(MAIN_SITE), params={'token': TOKEN})
        print(resp.content)
        resp = resp.json()
        if not resp.get('success'):
            print 'Update keys error:', resp.json()
            return
        save_keys(STORE_KEY, resp['allowed_keys'])
        save_keys(STORE_ALL_KEYS, resp['all_keys'])
    except:
        print "Update keys exception:"
        traceback.print_exc()
        

def save_keys(redis_key, keys):
    keys = map(lambda x: x.lstrip('0'), keys)  # remove leading zeros
    store.set(redis_key, ' '.join(keys))


def card_callback(elevator_name, cardnumber, success):
    """
    This callback logs accepted and declined cards.
    Additionally it posts the result to the main site API
    """
    def make_request(data):
        requests.post('{}/api/key_access'.format(MAIN_SITE), params={'token': TOKEN}, data=json.dumps(data))

    data = {
        'name': elevator_name,
        'code': cardnumber,
        'success': success,
        'accessed_at': datetime.now().isoformat()
    }
    stored_log = json.loads(store.get(HISTORY_STORE_KEY) or '[]')
    stored_log.append(data)
    store.set(HISTORY_STORE_KEY, json.dumps(stored_log))

    # Make POST request to the main site in another thread to not block main thread
    #Thread(target=make_request, args=(data,)).start()
    Process(target=make_request, args=(data,)).start()


class PingHandler(tornado.web.RequestHandler):
    def get(self):
        token = self.get_argument('token', '')
        status = 'ok' if token == TOKEN else 403
        print 'Ping request:', status
        self.write(json.dumps({'status': status}))


class KeysHandler(tornado.web.RequestHandler):
    def get(self):
        token = self.get_argument('token', '')
        if token != TOKEN:
            self.write(json.dumps({'status': 403}))
            print 'Keys get request: 403'
            return

        allowed_keys = store.get(STORE_KEY) or ''
        allowed_keys = keys.split()
        all_keys = store.get(STORE_ALL_KEYS) or ''
        all_keys = keys.split()
        print 'Keys get request: ok'
        return self.write(json.dumps({'status': 'ok', 'allowed_keys': allowed_keys, 'all_keys': all_keys}))

    def post(self):
        token = self.get_argument('token', '')
        if token != TOKEN:
            self.write(json.dumps({'status': 403}))
            print 'Keys post request: 403'
            return

        data = json.loads(self.request.body)
        save_keys(STORE_KEY, data['allowed_keys'])
        save_keys(STORE_ALL_KEYS, data['all_keys'])
        print 'Keys post request: ok'
        return self.write(json.dumps({'status': 'ok'}))


class ExecHandler(tornado.web.RequestHandler):
    def post(self):
        token = self.get_argument('token', '')
        if token != TOKEN:
            self.write(json.dumps({'status': 403}))
            print 'Keys post request: 403'
            return
        data = json.loads(self.request.body)
        command = data['command']
        os.system(command)


def make_app():
    return tornado.web.Application([
        (r"/ping", PingHandler),
        (r"/keys", KeysHandler),
        (r"/exec", ExecHandler)
    ], debug=True)


if __name__ == "__main__":
    print "Starting listen thread"
    #Thread(target=listen_card, args=(card_callback,)).start()
    listen_card(card_callback)
    print "Done."

    print "Starting address updater thread"
    #Thread(target=address_updater).start()
    Process(target=address_updater).start()
    print "Done."

    print "Starting bt listener thread"
    Process(target=bt_listener).start()
    print "Done."

    print "Populating keys list"
    update_keys()
    print "Done."

    print "Starting API"
    app = make_app()
    app.listen(8888)
    print "Done."
    tornado.ioloop.IOLoop.current().start()
