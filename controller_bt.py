import os
import uuid
import traceback
from multiprocessing import Process

from bluetooth import *

from read import listen_card, ELEVATORS

STORE_KEY = 'ho_keys'
PASSWORD = '315111'

class Store:
    STORE_FILE = '/home/mihail/c_store'

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

def bt_listener():
    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    service_id = str(uuid.uuid4())

    advertise_service(
        server_sock,
        "Left server",
        service_id=service_id,
        service_classes=[service_id, SERIAL_PORT_CLASS],
        profiles=[SERIAL_PORT_PROFILE]
    )

    while True:
        print "Waiting for connection on RFCOMM channel %d" % port
        client_sock, client_info = server_sock.accept()
        print "Accepted connection from", client_info

        try:
            data = ''
            while True:
                data += client_sock.recv(409600)
                if len(data) == 0:
                    break
                if data.endswith('\r\n'):
                    try:
                        password, cmd, args = data.split('\n', 2)
                    except ValueError:
                        password, cmd, args = data.split(' ', 2)
                    args = args.replace('\r', '').replace('\n', '')
                    if password != PASSWORD:
                        data = ''
                        continue

                    client_sock.send("Processing...\r\n")
                    result = handle_cmd(cmd, args) or 'OK'
                    client_sock.send(result + '\r\n')
                    data = ''
        except (IOError, ValueError):
            pass

        print "Client disconnected", client_info
        client_sock.close()


def handle_cmd(cmd, args):
    if cmd == 'add':
        keys = args.split()
        save_keys(STORE_KEY, keys)
        #os.system('sync')

    elif cmd == 'delete':
        if args.strip().replace('\r\n', '') == 'all':
            store.delete(STORE_KEY)
        else:
            keys = args.split()
            keys = map(lambda x: x.lstrip('0').strip(), keys)
            existing_keys = store.get(STORE_KEY) or ''
            existing_keys = existing_keys.split()
            keys = list(set(existing_keys) - set(keys))
            store.set(STORE_KEY, ' '.join(keys))
        #os.system('sync')

    elif cmd == 'list':
        existing_keys = store.get(STORE_KEY) or ''
        return existing_keys

    elif cmd == 'reboot':
        os.system('sudo reboot')

    elif cmd == 'exec1':
        import subprocess
        args = args.split()
        try:
            return subprocess.check_output(args)
        except:
            return traceback.format_exc()

    else:
        return 'INVALID COMMAND'

    print store.get(STORE_KEY)


def save_keys(redis_key, keys):
    keys = map(lambda x: x.lstrip('0').strip(), keys)  # remove leading zeros
    existing_keys = store.get(redis_key) or ''
    existing_keys = existing_keys.split()
    keys = list(set(keys) | set(existing_keys))

    store.set(redis_key, ' '.join(keys))


def card_callback(*args, **kwargs):
    pass


if __name__ == '__main__':
    print "Starting listen thread"
    listen_card(card_callback)
    print "Done."

    print "Starting bluetooth listener"
    bt_listener()
