# Simulator for the card game smear

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/pydealer")

from pysmear import smear_simulator


# Change this to run one test with debug output or 100 tests with no output
one_test=False
one_test=True

# Change this to enable teams. 0=no teams
num_teams=0

# Change this to play with more or less players
num_players=3

# Change this to play to a higher score (games take longer, but smarter AI tends to win more)
score_to_play_to=11

# Change this to log all stats to database on localhost
log_to_db = True

def main():
    if one_test:
        num_runs = 1
        debug=True
    else:
        num_runs = 100
        debug=False
    print "Setting up..."
    sim = smear_simulator.SmearSimulator(debug=debug, num_teams=num_teams, num_players=num_players, score_to_play_to=score_to_play_to, log_to_db=log_to_db)
    if len(sys.argv) > 1:
        num_runs = int(sys.argv[1])
    sim.run(num_runs)
    print "Generating stats..."
    print sim.stats()

if __name__ == "__main__":
    main()
