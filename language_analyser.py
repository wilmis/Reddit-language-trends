#!/usr/bin/env python3

#import reddit_crawler

import argparse
import uuid


class Post:
    """ Representing data held in posts"""

    def __init__(self, tokens, time, user, is_comment, url):
        """Initiate with data about the post obtained from crawler"""
        self.id = uuid.uuid4().hex
        self.tokens = tokens
        self.time = time
        self.user = user
        self.is_comment = is_comment
        self.url = url
        # TODO: add language?

        # Feature representation of the post
        self.analyzed_data = {}

        # Analyzed data with reduced dimensionality
        self.reduced_data = ()

class Corpus:
    def __init__(self, subreddit):
        self.subreddit = subreddit
        self.posts = []  # This is a list so we can sort it later

    def add_post(self, post):
        self.posts.append(post)

    def build(self):
        """
        Collects and generates a tokenized corpus for the given subreddit
        using the reddit_crawler
        """

        # FIXME: this is just a temporary structure for the corpus.
        post_a = Post(["today", "i", "learned", "you", "eat", "popcorn", "microwaved"], 13572134687, "axelwickm", False,
                      "https://www.reddit.com/r/CasualConversation/comments/95hpj2/today_i_learned_that_you_eat_popcorn_microwaved/")
        self.add_post(post_a)

        post_b = Post(["popcorn", "is", "the", "best", "thing", "since", "sliced", "bread"], 135721842345,
                      "thisisbillgates", True,
                      "https://www.reddit.com/r/CasualConversation/comments/95hpj2/today_i_learned_that_you_eat_popcorn_microwaved/comments=53774")
        self.add_post(post_b)

    def sort_posts(self):
        """ TODO:sort posts with oldest first """
        pass

    def perform_analysis(self):
        """
        Perform various analyses on the data.
        Save a high dimensional representation each post
        """

        self.posts[0].analyzed_data = {"sentiment": [0.5, 0.1, 0.3], "length": 30, "complexity": 0.92}
        self.posts[1].analyzed_data = {"sentiment": [0.8, 0.2, 0.8], "length": 10, "complexity": 0.12}

    def reduce_data_dimensions(self):
        """
        Uses a dimensionality reduction algorithm to convert the high dimensional into
        2D points for every post.
        Returns a list of these 2D points.
        """

        self.posts[0].reduced_data = (0.3, 0.7)
        self.posts[1].reduced_data = (0.8, 0.5)


def main(subreddits):
    """ Generate, analyze, cluster and visualize data from given subreddits """

    corpuses = {}
    for subreddit in subreddits:
        # The data is collected from reddit and corpuses are stored in a dictionary
        print("Creating corpus: /r/"+subreddit)
        corpus = Corpus(subreddit)
        corpus.build()

        # Features are extracted from the corpuses and stored in as high
        # dimensional representations
        print("Analyzing corpus: /r/" + subreddit)
        corpus.perform_analysis()

        # This data is then converted into 2D points
        print("Reducing corpus representation: /r/" + subreddit)
        corpus.reduce_data_dimensions()

        # Save to dictionary and to file in /data/ directory
        corpuses[subreddit] = corpus
        print("Saving clustered corpus: /r/" + subreddit + "\n\n")
        # TODO: save to file

    # TODO: open HTTP server

    # TODO: tell default browser to open web server address and visualize data


if __name__ == "__main__":
    # Figure out what algoritms the user wants to analyze.
    # This is fed into the program by typing for example:
    # python language_analyzer.py aww me_irl
    parser = argparse.ArgumentParser(description="What to analyse")
    parser.add_argument('subreddit', metavar="s", type=str, nargs='*',
                        help='What subreddits to analyze')
    args = parser.parse_args()
    subreddits = args.subreddit
    # If no subreddits, use /r/sweden as default
    if len(subreddits) == 0:
        subreddits.append("sweden")

    main(subreddits)
