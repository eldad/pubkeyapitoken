# pubkeyapitoken

PoC code for getting an api-token with a public/private key authentication.

Server authentication can be added with HTTPS reverse proxy.

## Make keys

```
$ cd keys
$ ./make_keys.sh
```

## Start Server

```
$ pipenv install
$ export FLASK_APP=server
$ pipenv run flask run
```

## Get token and data

```
$ ./get_token.sh someone keys/client.key
$ ./get_token.sh someoneelse keys/client2.key
```
