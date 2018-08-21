#!/usr/bin/env python3
#
# Copyright (c) 2018 Eldad Zack
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from flask import Flask, request
from M2Crypto import RSA, X509

import time
import json
import base64
import uuid

def create_app():
    app = Flask(__name__)

    with app.app_context():
        REPLAY_PROTECTION_SECS = 10

        server_key = RSA.load_key("keys/server.key")

        users = {
            'someone': {
                'cert': 'keys/client.pub',
                'data': 'hello there'
            },
            'someoneelse': {
                'cert': 'keys/client2.pub',
                'data': 'hi :)'
            },
        }

    @app.route("/token", methods=['POST'])
    def token():
        reqtime = time.time()

        message = base64.b64decode(request.form['message'])
        cleartext = server_key.private_decrypt(message, RSA.pkcs1_padding)

        tokenreq = json.loads(cleartext.decode('utf-8'))

        if abs(reqtime - int(tokenreq['timestamp'])) > REPLAY_PROTECTION_SECS:
            return ('No way', 500)  # don't do this in production.

        username = tokenreq['username']

        # Image this is a database access.
        if (username not in users):
            return ('No such user', 500)

        user = users[username]

        user_cert = X509.load_cert(user['cert'])
        user_pubkey = user_cert.get_pubkey().get_rsa()
        user['token'] = str(uuid.uuid4())

        print('User token: {}'.format(user['token']))

        response = user_pubkey.public_encrypt(user['token'].encode(), RSA.pkcs1_padding)
        return (base64.b64encode(response), 200)

    @app.route("/apicall/<username>", methods=['GET'])
    def apicall(username):
        if username not in users:
            return ('Token error', 403)

        user = users[username]

        if 'token' not in user:
            return ('Token error', 403)

        token = request.args.get('token', None)
        if token is None:
            return ('Token error', 403)

        if token != user['token']:
            return ('Token error', 403)

        return user['data']

    # create_app
    return app
