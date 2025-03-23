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

Deploy to test:

```
fly deploy -c config/test.fly.toml
```

Deploy to prod:

```
fly deploy
```

# Accessing Prod

```
fly ssh console
```

# Database Disk Management

## Delete the old games

Note: this might take a while, use `caffeinate -ims` to keep mac alive

```
fly ssh console
python manage.py cleanup_old_games
```

## Vacuum to reclaim space in database

```
fly ssh console
apt-get install -y postgresql-client
python manage.py dbshell
vacuum full;
```

## Check to see which table is taking up the most space

```
fly ssh console
apt-get install -y postgresql-client
python manage.py dbshell

SELECT
    table_name,
    pg_size_pretty(table_size) AS table_size,
    pg_size_pretty(indexes_size) AS indexes_size,
    pg_size_pretty(total_size) AS total_size
FROM (
    SELECT
        table_name,
        pg_table_size(table_name) AS table_size,
        pg_indexes_size(table_name) AS indexes_size,
        pg_total_relation_size(table_name) AS total_size
    FROM (
        SELECT ('"' || table_schema || '"."' || table_name || '"') AS table_name
        FROM information_schema.tables
    ) AS all_tables
    ORDER BY total_size DESC
) AS pretty_sizes;
```

# Changing memory for database VM

```
fly machine -a playsmear-db update --vm-memory 512
```

# Extend DB volume

```
fly -a playsmear-db vol list
fly -a playsmear-db vol extend <volume id> -s 3

# Restarting the machine might be necessary
fly -a playsmear-db machine list
fly -a playsmear-db machine stop <machine id>
fly -a playsmear-db machine start <machine id>
```

# Restart DB

```
fly pg restart -a playsmear-db --skip-health-checks --force
```

# Adding secrets

```
fly secrets set SECRET_NAME=123abc
```
