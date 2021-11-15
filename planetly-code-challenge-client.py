import requests
import random
import string
import time
import json
import sys
import argparse

#import socket

# TODO develop the API network address finder

# Function to find web application address on the network
# def get_ip():
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         # doesn't even have to be reachable
#         s.connect(('255.255.255.255', 1))
#         IP = s.getsockname()[0]
#     except Exception:
#         print("Unable to find the API endpoint on the network.")
#         s.close()
#         exit()
#     finally:
#         s.close()
#     return IP

def main(endpoint='127.0.0.1',port='8080'):
    # Generating random 10 char sting for the x-secret-key
    letters = string.ascii_lowercase
    x_secret_key = ''.join(random.choice(letters) for i in range(10))

    throttling_period = 60

    # URL variables to be easier to change parameters like endpoint, port or path for example
    path = 'ping'
    protocol = 'http'
    ping_headers = {"x-secret-key": x_secret_key, "Content-Type": "application/json"}
    ping_payload = '{"request":"ping"}'

    URL = protocol + '://' + endpoint + ':' + port + '/' + path 

    while True:
        #init = time.time()
        response = requests.post(URL,data=ping_payload,headers=ping_headers)
        print(json.dumps(json.loads(response.text), indent=4, sort_keys=True))
        if response.status_code != 200 and response.json().get("throttle_age") != None:
            print("Waiting for throttling time window (" + str(throttling_period) + " seconds). Requests will be sent after throttling expired.")
            time.sleep(throttling_period)
            
        time.sleep(1 - response.elapsed.total_seconds())
        #print("Request duration: " + str(time.time() - init))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI tool to interact with the ping-pong web API.')
    parser.add_argument('--endpoint', dest='endpoint', default='127.0.0.1',
                        help='the ping-pong web API hostname or IP (default: 127.0.0.1)')
    parser.add_argument('--port', dest='port', default='8080',
                        help='the ping-pong web API port (default: 8080)')

    args = parser.parse_args()

    main(args.endpoint,args.port)