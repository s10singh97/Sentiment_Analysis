import os
import sys

from analyzer import Analyzer
from termcolor import *
import colorama
colorama.init()

def main():

    # ensure proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python smile.py word")

    # absolute paths to lists
    positives = os.path.join(sys.path[0], "positive-words.txt")
    negatives = os.path.join(sys.path[0], "negative-words.txt")

    # instantiate analyzer
    analyzer = Analyzer(positives, negatives)

    # analyze word
    score = analyzer.analyze(sys.argv[1])
    if score > 0.0:
        cprint(":)", "green")
    elif score < 0.0:
        cprint(":(", "red")
    else:
        cprint(":|", "yellow")

if __name__ == "__main__":
    main()
