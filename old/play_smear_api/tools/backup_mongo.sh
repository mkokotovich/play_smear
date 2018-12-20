#!/bin/bash
set -xeuo pipefail

if [ $# -ne 1 ] ; then
    echo "Error, please pass the directory to dump the backup in"
    exit 1
fi

dumpdir=$1

if [ ! -d ${dumpdir} ] ; then
    echo "Error, ${dumpdir} is not a valid directory"
    exit 1
fi

# From https://gist.github.com/leesei/6668590
# [schema://][user[:password]@]host[:port][/path][?[arg1=val1]...][#fragment]
function uri_parser() {
    # uri capture
    uri="$@"

    # safe escaping
    uri="${uri//\`/%60}"
    uri="${uri//\"/%22}"

    # top level parsing
    pattern='^(([a-z]{3,7})://)?((([^:\/]+)(:([^@\/]*))?@)?([^:\/?]+)(:([0-9]+))?)(\/[^?]*)?$'
    [[ "$uri" =~ $pattern ]] || return 1;

    # component extraction
    uri=${BASH_REMATCH[0]}
    uri_schema=${BASH_REMATCH[2]}
    uri_address=${BASH_REMATCH[3]}
    uri_user=${BASH_REMATCH[5]}
    uri_password=${BASH_REMATCH[7]}
    uri_host=${BASH_REMATCH[8]}
    uri_port=${BASH_REMATCH[10]}
    uri_path=${BASH_REMATCH[11]}

    # return success
    return 0
}

if [ -z "${MONGODB_URI}" ] ; then
    export MONGODB_URI=$(heroku config --app playsmear | sed -ne 's/MONGODB_URI: \(.*\)/\1/p')
fi

if [ -z "${MONGODB_URI}" ] ; then
    echo "Error, could not find mongodb_uri"
    exit 1
fi

uri_parser "${MONGODB_URI}"

# Remove leading slash from path
database=${uri_path:1}

docker run -v ${dumpdir}:/mongodump mongo:latest mongodump -h ${uri_host}:${uri_port} -d ${database} -u ${uri_user} -p ${uri_password} -o /mongodump

# To restore:
# docker run -v ${dumpdir}:/mongodump mongo:latest mongorestore -h ${uri_host}:${uri_port} -d ${database} -u ${uri_user} -p ${uri_password} /mongodump/*

