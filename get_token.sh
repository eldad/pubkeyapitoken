#!/bin/bash
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

scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set -eu

username=${1?must provide username}
keyfile=${2?must provide keyfile}

server_pub_key="${scriptdir}/keys/server.pub"

server_url="http://localhost:5000"

# shellcheck disable=SC2089
message='{"username": "'"${username}"'", "timestamp": '$(date +%s)'}'

echo "Message: ${message}"

crypttext=$(echo -n "${message}" | openssl rsautl -encrypt -certin -inkey "${server_pub_key}" | base64 -w0)

echo "Crypttext: ${crypttext}"

token_response=$(curl -sSL "${server_url}/token" -X POST --data-urlencode "message=${crypttext}")

echo "Server responded with: ${token_response}"

token=$(echo "${token_response}" | base64 -d | openssl rsautl -decrypt -inkey "${keyfile}")

echo "Token: ${token}"

data=$(curl -sSL "${server_url}/apicall/${username}?token=${token}")

echo "Data: ${data}"
