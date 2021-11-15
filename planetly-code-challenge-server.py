import flask
from flask import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import math

# Function to get specific 'x-secret-key' header from request for the thottling logic
def header_limit_function():
    return flask.request.headers.get('x-secret-key')

app = flask.Flask(__name__)
limiter = Limiter(app)
#app.config["DEBUG"] = True

# Error handling function triggered when exeding the request limits to provide friendly message to the client
@app.errorhandler(429)
def ratelimit_handler(e):
    global throttle # Flag to define the first time requests have been throttled to start timing the throttle age
    global throttle_init
    if throttle == False:
        throttle_init = time.time() # Time of the first throttled request
        throttle = True
        throttle_age = 0
    else:
        # Throttle age rounded up to an integer number because for the 2 requests per second limitation the rounded 
        # number to an integer was usually equal to zero (for example: throttle_age = 0.4 seconds)
        throttle_age = math.ceil(time.time() - throttle_init)  

    # Response created with the friendly message, thottle age and a HTTP error code of 429 TOO MANY REQUESTS so the 
    # clients can have more information on the throttled requests
    return flask.make_response(
            flask.jsonify({"message": "You have exceeded your request-limits.", "throttle_age" : throttle_age})
            , 429
    )

# API ping route definition
@app.route('/ping', methods=['POST'])

# Limit a maximum of 2 requests per second regardless of the x-secret-key
@limiter.limit("2/second", get_remote_address)
# Limit a maximum of 10 requests per minute for each x-secret-key header
@limiter.limit("10/minute", header_limit_function)

# Main function for the /ping route
def home():
    # Flag variable to define when requests have been throttled
    # TODO design a better solution for the computation of the trottle age in order to avoid using global variable
    global throttle
    throttle = False
    
    # Checking the request's 'x-secret-key' header type and error handling response
    if type(flask.request.headers.get('x-secret-key')) != str:
        return flask.make_response(
            flask.jsonify({"message": "Error! Header x-secret-key is required"})
            , 400
        )
    # Checking if the request has a payload in a JSON format as required and error handling response
    elif flask.request.json == None:
        return flask.make_response(
            flask.jsonify({"message": "Error! Request payload is required"})
            , 400
        )
    # Checking if the request's payload key: 'request' is equal to ping as required and error handling response
    elif flask.request.json['request'] != 'ping':
        return flask.make_response(
            flask.jsonify({"message": "Error! Wrong request payload"})
            , 400
        )
    # If the request's header and payload are correct a simple 'pong' response message is return in JSON format
    else:
        return flask.jsonify({"response": "pong"})

# Run Flask API for all network local address and on port 8080 instead of default 127.0.0.1:5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)