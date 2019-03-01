#!/usr/bin/env python3

import pushsift_reddit_crawler as prc

import argparse
import uuid
import pickle
import os
import datetime as dt

class Post:
    """ Representing data held in posts"""

    def __init__(self, tokens, time, user, is_comment, parentPost, url):
        """Initiate with data about the post obtained from crawler"""
        self.id = uuid.uuid4().hex
        self.tokens = tokens
        self.time = time
        self.user = user
        self.is_comment = is_comment
        self.parentPost = parentPost
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
        self.year = 2014
        self.month = 1
        self.day = 1
        self.subLimit = 10

    def build(self, reddit, pushshift_api, time_start, time_stop, submissions):
        """
        Collects and generates a tokenized corpus for the given subreddit
        using the reddit_crawler
        """

        # pushsift_reddit_crawler.py == prc
        for t in range(time_start, time_stop, int((time_stop-time_start)/submissions)):
            print("\r{0} %".format(int((t-time_start)/(time_stop-time_start)*100)), end="\r")
            q = prc.query(reddit, pushshift_api, t, self.subreddit, 1)
            for p in q:
                if len([c for x in self.posts if x.id == p[0].id]) == 0: # FIXME: this is slow and ugly
                    self.posts.append(p[0])
                else:
                    print("Got the same post twice")
        print("done")

        print(len(self.posts)) 

    def sort_posts(self):
        self.posts.sort(key=lambda x:x.time)

    def perform_analysis(self):
        """
        Perform various analyses on the data.
        Save a high dimensional representation each post
        """

        """self.posts[0].analyzed_data = {"sentiment": [0.5, 0.1, 0.3], "length": 30, "complexity": 0.92}
        self.posts[1].analyzed_data = {"sentiment": [0.8, 0.2, 0.8], "length": 10, "complexity": 0.12}"""

    def reduce_data_dimensions(self):
        """
        Uses a dimensionality reduction algorithm to convert the high dimensional into
        2D points for every post.
        Returns a list of these 2D points.
        """

        self.posts[0].reduced_data = (0.3, 0.7)
        self.posts[1].reduced_data = (0.8, 0.5)

def corpus_from_file(path):
    print("Using existsing corpus file: "+path)
    corpus_file = open(path, mode='rb')
    corpus = pickle.load(corpus_file)
    corpus_file.close()
    return corpus

def corpus_to_file(corpus, path):
    print("Saving built corpus to: "+path)
    corpus_file = open(path, mode='wb')
    pickle.dump(corpus, corpus_file)
    corpus_file.close()

def remove_corpus_file(path):
    if os.path.exists(path):
        print("Removing corpus "+path)
        os.remove(path)

def main():
    """ Generate, analyze, cluster and visualize data from given subreddits """

    # Figure out what algoritms the user wants to analyze.
    # This is fed into the program by typing for example:
    # python language_analyzer.py aww me_irl
    parser = argparse.ArgumentParser(description="What to analyse")
    parser.add_argument('subreddit', metavar="s", type=str, nargs='*',
                        help='What subreddits to analyze')
    args = parser.parse_args()
    subreddits = args.subreddit
    # If no subreddits, use /r/worldnews as default
    if len(subreddits) == 0:
        subreddits.append("worldnews")

    # TODO: add to argument parser
    posts = 500
    read_from_cache = False
    save_to_cache = True
    remove_previous_stage_caches = True

    save_cache_to_server = False # TODO
    get_cache_from_server = False # TODO

    reddit, pushshift_api = prc.make_reddit_instance()

    corpuses = {}
    for subreddit in subreddits:
        cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "caches")
        built_path = os.path.join(cache_path, subreddit+"_1built_"+str(posts)+".pickle")
        analyzed_path = os.path.join(cache_path, subreddit+"_2analyzed_"+str(posts)+".pickle")
        reduced_path = os.path.join(cache_path, subreddit+"_3reduced_"+str(posts)+".pickle")

        if os.path.isfile(reduced_path) and read_from_cache:
            corpus = corpus_from_file(reduced_path)
        else:
            if os.path.isfile(analyzed_path) and read_from_cache:
                corpus = corpus_from_file(analyzed_path)
            else:
                if os.path.isfile(built_path) and read_from_cache:
                    corpus = corpus_from_file(built_path)
                else:
                    # The data is collected from reddit and corpuses are stored in a dictionary
                    print("\nCreating corpus: /r/"+subreddit)
                    corpus = Corpus(subreddit)
                    
                    time_start = int(dt.datetime(2012, 2, 4).timestamp())
                    time_stop = int(dt.datetime(2019, 2, 4).timestamp())
                    corpus.build(reddit, pushshift_api, time_start, time_stop, 50)

                    if save_to_cache:
                        corpus_to_file(corpus, built_path)

                # Features are extracted from the corpuses and stored in as high
                # dimensional representations
                print("\nAnalyzing corpus: /r/" + subreddit)
                corpus.perform_analysis()

                if save_to_cache:
                        corpus_to_file(corpus, analyzed_path)

                if remove_previous_stage_caches:
                    remove_corpus_file(built_path)

            # This data is then converted into 2D points
            print("\nReducing corpus representation: /r/" + subreddit)
            corpus.reduce_data_dimensions()

            if save_to_cache:
                corpus_to_file(corpus, reduced_path)

            if remove_previous_stage_caches:
                remove_corpus_file(built_path)
                remove_corpus_file(analyzed_path)



        corpuses[subreddit] = corpus


    # TODO: open HTTP server

    # TODO: tell default browser to open web server address and visualize data


if __name__ == "__main__":
    main()
