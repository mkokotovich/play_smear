import urllib2
import json
import subprocess
import time

travis_base_url="https://api.travis-ci.org/repos/mkokotovich/pysmear"

def main():
    # find the git commit id of master
    master_commit_id = subprocess.check_output("git rev-parse master", shell=True).strip()

    while True:
        # find the last build
        req = urllib2.Request(travis_base_url)
        req.add_header('Accept', 'application/vnd.travis-ci.2+json')
        resp = urllib2.urlopen(req)

        data = json.load(resp)

        last_build_state=data["repo"]["last_build_state"]

        last_build_id=data["repo"]["last_build_id"]

        # Then find the commit id for that build
        req = urllib2.Request(travis_base_url + "/builds/" + str(last_build_id))
        req.add_header('Accept', 'application/vnd.travis-ci.2+json')
        resp = urllib2.urlopen(req)
        data = json.load(resp)

        travis_commit_id = data["commit"]["sha"]

        if master_commit_id == travis_commit_id:
            # Commit's match
            print "Current commit: " + last_build_state
            if last_build_state == "passed" or last_build_state == "failed":
                return
        else:
            print "Current commit has NOT been picked up by travis yet"
        time.sleep(5)


if __name__ == "__main__":
    main()
