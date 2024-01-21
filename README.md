[![Build Status](https://travis-ci.org/mkokotovich/play_smear.svg?branch=master)](https://travis-ci.org/mkokotovich/play_smear)
# play\_smear

Play the card game smear online:
http://www.playsmear.com

# Local Development

```
docker compose build
docker compose up
```

The UI and the API are both served from `http://localhost:8000`

Alternatively, the UI can be run using `yarn start`

Install precommit hooks

```
pre-commit install --install-hooks
```

# Deployment

`flyctl deploy`

# Accessing Prod

```
fly ssh console
```
