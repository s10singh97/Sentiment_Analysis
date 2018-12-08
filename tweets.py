import sys
import os
import helpers
from analyzer import Analyzer
from termcolor import *
import colorama
colorama.init()

# ensure proper usage
if len(sys.argv) != 2:
    sys.exit("Usage: python tweets.py twitter_handle")

app = sys.argv[1]

# absolute paths to lists
positives = os.path.join(sys.path[0], "positive-words.txt")
negatives = os.path.join(sys.path[0], "negative-words.txt")

tweets, photo = helpers.get_user_timeline(app, 50)

if tweets == None:
    sys.exit("Error, unable to access user's tweets")

# instantiate analyzer
analyzer = Analyzer(positives, negatives)

# analyze word
i = 1
for tweet in tweets:
    c = analyzer.analyze(tweet)
    print(str(i) + "." + "\t" + tweet, end=" ")
    i += 1
    if c > 0:
        cprint(":)", "green")
    elif c < 0:
        cprint(":(", "red")
    else:
        cprint(":|", "yellow")