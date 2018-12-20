import os
import errno
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from cycler import cycler
except:
    pass

class ScoreGraphManager():
    def __init__(self, score_to_play_to):
        self.scores = {}
        self.score_to_play_to = score_to_play_to
        self.label_constants = {
                11:[ 15, 8 ],
                15:[ 20, 13],
                21:[ 25, 15]
                }
        self.colors= [
                "blue",
                "orange",
                "plum",
                "sienna",
                "khaki",
                "linen",
                "cyan",
                "green"
                ]


    def reset(self):
        self.scores = {}


    def add_new_hand_to_scores(self, graph_prefix, current_scores):
        if graph_prefix not in self.scores.keys():
            self.scores[graph_prefix] = [ [x] for x in current_scores ] 
        else:
            for i in range(0, len(current_scores)):
                self.scores[graph_prefix][i].append(current_scores[i])
        return self.scores[graph_prefix]


    def remove_game_from_scores(self, graph_prefix):
        del self.scores[graph_prefix]


    def create_directory_if_needed(self, filename):
        dirname = os.path.dirname(filename)
        try:
            os.makedirs(dirname)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


    def export_graph(self, graph_prefix, filename, current_scores, player_names):
        scores_so_far = self.add_new_hand_to_scores(graph_prefix, current_scores)

        self.create_directory_if_needed(filename)

        # Generate X-axis data
        hands = range(0, len(scores_so_far[0]))

        # Set the line colors
        plt.rc('axes', prop_cycle=(cycler('color', self.colors)))

        # For each player, plot a line of their scores
        for i in range(0, len(player_names)):
            plt.plot(hands, scores_so_far[i], label=player_names[i])

        # Add a legend of the player names
        plt.legend(loc='upper left')

        # Set graph details
        ax = plt.gca()
        # Set Y axis limit
        try:
            ymax = self.label_constants[self.score_to_play_to][0]
        except:
            ymax = 15
        ax.set_ylim([-3, ymax])
        # Set Y axis label
        ax.set_ylabel("Points")
        # Set X axis limit and tick marks
        try:
            xmax = self.label_constants[self.score_to_play_to][1]
        except:
            xmax = 8
        x_tick_max=max(xmax, len(scores_so_far[0]) + 1)
        ax.set_xticks(range(0, x_tick_max))
        # Set X axis label
        ax.set_xlabel("Hand")

        # Save graph to file
        plt.savefig(filename)

        # Close graph
        plt.close()
