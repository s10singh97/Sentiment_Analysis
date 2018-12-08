import nltk

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""

        self.positives = []
        with open("positive-words.txt", "r") as word1:
            for line in word1:
                if line.startswith(";") or line.startswith(" "):
                    pass
                else:
                    self.positives.extend(line.split())

        self.negatives = []
        with open("negative-words.txt", "r") as word2:
            for line in word2:
                if line.startswith(";") or line.startswith(" "):
                    pass
                else:
                    self.negatives.extend(line.split())

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""

        c = 0
        tokenizer = nltk.tokenize.TweetTokenizer()
        tokens = tokenizer.tokenize(text)
        for token in tokens:
            if token in self.positives:
                c += 1

            elif token in self.negatives:
                c += (-1)

            else:
                c += 0

        return c

    def show(self):
        print(self.positives)
        print(self.negatives)