#!/usr/bin/env python3

import reddit_crawler

import argparse


def create_corpus(subreddit):
    """
    Collects and generates a tokenized corpus for the given subreddit
    using the reddit_crawler
    """

    # FIXME: this is just a temporary structure for the corpus.
    # It will also have to include time/date, link, user?, unique post id?
    return [["i", "really", "hate", "popcorn."],
            ["popcorn", "is", "the", "best", "thing",
             "since", "sliced", "bread"]]


def analyze_data(corpus):
    """
    Perform various analyses on the data.
    Return a highdimentional vector representation for each post
    """

    return [[0.5, 0.1, 0.3, 0.8, 0.3], [0.0, 0.8, 0.4, 0.2, 0.35]]


def cluster_data(representation):
    """
    Uses a clustering algorithm to convert the high dimensional into
    2D points for every post.
    Returns a list of these 2D points.
    """

    return [[0.1, 0.9], [0.5, 0.2]]


def main(subreddits):
    """ Generate, analyze, cluster and visualize data from given subreddits """

    # The data is collected from reddit and corpuses are stored in a dictionary
    corpuses = {}
    for subreddit in subreddits:
        print("Creating corpus: /r/"+subreddit)
        corpuses[subreddit] = create_corpus(subreddit)

    print("")

    # Features are extraced from the corpuses and stored in as high
    # dimensional representations
    representations = {}
    for subreddit, corpus in corpuses.items():
        print("Analyzing corpus; /r/"+subreddit)
        representations[subreddit] = analyze_data(corpus)

    print("")

    # This data is then converted into 2D points, and saved to a file with
    # other meta information
    for subreddit, representation in representations.items():
        # Run the clustering algorthim
        print("Clustering corpus representation: /r/"+subreddit)
        clustered = cluster_data(representation)

        # Save to file immediately to /data/ directory
        # We don't need it in the rest of the program
        print("Saving clustered corpus: /r/"+subreddit+"\n")
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
