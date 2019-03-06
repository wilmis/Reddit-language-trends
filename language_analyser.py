#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import reddit_crawler


import pushsift_reddit_crawler as prc
import dimensionality_reducer as dr
from start_server import start_server

import argparse
import uuid
import json
import os
import datetime as dt
from collections import Counter
import math
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
nltk.download('average_perceptron_tagger')

class Post:
    """ Representing data held in posts"""
    def __init__(self, tokens=None, time=None, user=None, is_comment=None, parentPost=None, url=None, upRatio=None):
        """Initiate with data about the post obtained from crawler"""
        self.id = uuid.uuid4().hex
        self.tokens = tokens
        self.time = time
        self.user = user
        self.is_comment = is_comment
        self.parentPost = parentPost
        self.url = url
        self.upRatio = upRatio

        self.sanitized_tokens = None


        # Feature representation of the post
        self.analyzed_data = {}

        # Analyzed data with reduced dimensionality
        self.reduced_data = ()

    @property
    def sanitized(self):
        bad_tokens = ["*", "~", "^","`", ">"]
        bad_combinations =  [["[", "deleted", "]"],
                             ["[", "raderat", "]"],
                             ["[", "borttagen", "]"],
                             [">","!"], ["!","<"]]

        if not hasattr(self, 'sanitized_tokens'):
            self.sanitized_tokens = None

        if self.sanitized_tokens is None:
            self.sanitized_tokens = []

            for token_sentence in self.tokens:
                sanitized_sentence = []

                # Remove single bad token
                sanitized_sentence = filter(lambda t: not t in bad_tokens, token_sentence)
                sanitized_sentence = list(sanitized_sentence)

                # Remove bad token combination
                for comb in bad_combinations:
                    next_index = 0
                    i = 0
                    while i != len(sanitized_sentence):
                        if sanitized_sentence[i] == comb[next_index]:
                            next_index += 1
                        else:
                            next_index = 0

                        if next_index == len(comb):
                            del sanitized_sentence[i-len(comb)+1:i+1]
                            i = i - len(comb)
                            next_index = 0
                        i += 1
                # This doesn't work when divided up into sentences.
                """
                # Remove links
                i = 0
                content_start, content_end = 0, 0
                next_index = 0
                while i != len(sanitized_sentence):
                    if next_index == 0 and sanitized_sentence[i] == "[":
                        next_index = 1
                        content_start = i + 1

                    if next_index == 1 and sanitized_sentence[i] == "]":
                        next_index = 2
                        content_end = i

                    if next_index == 2 and sanitized_sentence[i] == "(":
                        next_index = 3
                    else:
                        next_index = 0

                    if next_index == 3 and sanitized_sentence[i] == ")":
                        next_index = 0
                        keep = sanitized_sentence[content_start:content_end]
                        del sanitized_sentence[content_start-1, i+1]
                        sanitized_sentence += keep
                        i = content_start - 1

                    i += 1
                """

                if sanitized_sentence != []:
                    self.sanitized_tokens.append(sanitized_sentence)

        return self.sanitized_tokens


class Corpus:
    def __init__(self, subreddit=None):
        self.subreddit = subreddit
        self.posts = []

        self.time_start = None
        self.time_stop = None

        self.timespan = None
        self.reducer_steps = None
        self.reducer_epocs = None

    def build(self, reddit, pushshift_api, time_start, time_stop, submissions):
        """
        Collects and generates a tokenized corpus for the given subreddit
        using the reddit_crawler
        """

        self.time_start = time_start
        self.time_stop = time_stop

        # pushsift_reddit_crawler.py == prc
        for t in range(time_start, time_stop, int((time_stop-time_start)/submissions)):
            print("\r{0} %".format(int((t-time_start)/(time_stop-time_start)*100)), end="\r")
            q = prc.query(reddit, pushshift_api, t, self.subreddit, 1)
            for p in q:
                if len([1 for x in self.posts if x.time == p[0].time]) == 0: # FIXME: this is slow and ugly
                    self.posts.append(p[0])
                else:
                    print("Got the same post twice")
        print("done")

        print(len(self.posts))

        for t in range(time_start, time_stop, int((time_stop-time_start)/submissions)):
            print("\r{0} %".format(int((t-time_start)/(time_stop-time_start)*100)), end="\r")
            q = prc.query(reddit, pushshift_api, t, self.subreddit, 1)
            for p in q:
                if len([1 for x in self.posts if x.time == p[0].time]) == 0: # FIXME: this is slow and ugly
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

        vocabulary = Counter()
        analyze = SentimentIntensityAnalyzer()

        i = 0

        tagset_verb = ['VB','VBZ','VBD','VBN', 'VBG', 'VBP']
        tagset_adverb = ['RB','RBR','RBS']
        tagset_nouns = ['NN','NNP','NNS']
        tagset_adjectives = ['JJ','JJS','JJR']
        i = 0
        for post in self.posts:
            print("\r{0} %".format(int(i/len(self.posts)*90)), end="\r")
            i += 1
            ## Tuples: First index is posttitle + self text
            ##         Second index is comments
            #polarity_tuples = analyze.polarity_scores(" ".join(post.tokens))
            #print(polarity_tuples)
            sentiments = {"neg":[], "neu":[], "pos":[], "compound":[]}
            flat_sanitized = [item for sublist in post.sanitized for item in sublist]
            print(flat_sanitized)
            print(post.url)

            average_token_length = 0
            for token in flat_sanitized:
                vocabulary[token] += 1
                average_token_length += len(token)

            average_token_length = 0
            if flat_sanitized != []:
                average_token_length /= len(flat_sanitized)

            average_sentence_length = 0


            for sentence in post.sanitized:
                average_sentence_length += len(sentence)

                polarity_text = analyze.polarity_scores(" ".join(sentence))
                tagged_sentence = nltk.pos_tag(sentence)
                for key, value in polarity_text.items():
                    sentiments[key].append(value)



            average_token_length = 0
            if flat_sanitized != []:
                average_sentence_length /= len(post.sanitized)

            for key, value in sentiments.items():
                if len(sentiments[key]) == 0:
                    sentiments[key] = 0
                else:
                    sentiments[key] = sum(sentiments[key]) / len(sentiments[key])



            post.analyzed_data = {
                "Post length" : len(flat_sanitized),
                "Average sentence length" : average_sentence_length,
                "Average token length" : average_token_length,

                "Sentiment negative" : sentiments["neg"], # Will these cause problems with t-sne because they are too similar?
                "Sentiment neutral" : sentiments["neu"],
                "Sentiment positive" : sentiments["pos"],

                "Upvote ratio" : post.upRatio
            }

            #print("Sentiments:", sentiments)
            #polarity_comment_thread = analyze.polarity_scores(" ".join(post[1].tokens))
            #print("Sentiment for post : " + str(polarity_title_text) + '\n' + "Sentiment for comments : " + str(polarity_comment_thread))

        total = sum(vocabulary.values(), 0.0)
        for key in vocabulary:
            vocabulary[key] = math.log(vocabulary[key]/total)

        i = 0
        for post in self.posts:
            print("\r{0} %".format(int(i/len(self.posts)*10+90)), end="\r")
            i += 1

            flat_sanitized = [item for sublist in post.sanitized for item in sublist]
            average_probability = 0
            for token in flat_sanitized:
                average_probability += vocabulary[token]
            average_probability /= len(flat_sanitized)

            post.analyzed_data["Average word probability"] = average_probability
        pos_counter = Counter()
         ##TODO: FÅ detta att fungera
        for word in tagged_sentence:
            if word[1] in tagset_verb:
                pos_counter['VERB'] += 1
                continue
            elif word[1] in tagset_adverb:
                pos_counter['ADVERB'] += 1
                continue
            elif word[1] in tagset_adjectives:
                pos_counter['ADJECTIVE'] += 1
                continue
            elif word[1] in tagset_nouns:
                pos_counter['NOUNS'] += 1

            for x in pos_counter.most_common(1):
                print(x[1])
                most_common = x[1]
                print('----------------')
                print(x[1])
                post.analyzed_data["Most used word class "] = most_common

        ## Skapar dictionary med alla CAPS ord och deras frekvens.
            caps_count = Counter()
            for post in self.posts:
                flat_sanitized = [item for sublist in post.sanitized for item in sublist]
                for token in flat_sanitized:
                    if token == 'I':
                        continue
                    if token.isupper() == True:
                        caps_count[token] +=1
                    caps_count.pop([caps])
                    caps = caps_count
                    post.analyzed_data["Amount of CAPS words"] = caps
            ##Räknar antalet länkar i post
            www_count = 0

            for post in self.posts:
                flat_sanitized = [item for sublist in post.sanitized for item in sublist]
                for token in flat_sanitized:
                    if token == 'www':
                        www_count += 1
                    links = www_count
                    post.analyzed_data["Amount of World Wide Web links"] = links

            print("\n")
            print(" ".join(flat_sanitized))
            for key, value in post.analyzed_data.items():
                print(key, ":", value)




        print(tagged_sentence)
        print(pos_counter.most_common(1))
        print(pos_counter.most_common(1)[0][1])

        print("done")
        ##python language_analyser.py AskReddit --starttime 2014-05-02T05:33+0000 --endtime 2015-05-02T05:33+0000 -n 1000 -rw




        # Räknar antalet länkar som World Wide Web länkar som uppstår i texten som analyseras.



        #print({"Sentence :":vs, })

        """self.posts[0].analyzed_data = {"sentiment": [0.5, 0.1, 0.3], "length": 30, "complexity": 0.92}
        self.posts[1].analyzed_data = {"sentiment": [0.8, 0.2, 0.8], "length": 10, "complexity": 0.12}"""

    def reduce_data_dimensions(self, timespan, steps, epochs, perplexity):
        """
        Uses a dimensionality reduction algorithm to convert the high dimensional into
        2D points for every post.
        Returns a list of these 2D points.
        """

        self.timespan = dt.timedelta(days=timespan).total_seconds()
        self.reducer_steps = steps
        self.reducer_epocs = epochs

        self.sort_posts()

        try:
            dr.Dynamic_tSNE_reduce_dimensions(self, dt.timedelta(days=timespan).total_seconds(), steps, epochs, perplexity)
        except AssertionError:
            print("Can't reduce data. Is theano installed?")


def corpus_from_file(path):
    print("Using existsing corpus file: "+path)
    corpus_file = open(path, mode='r')
    jcorpus = json.load(corpus_file)
    corpus_file.close()

    posts = []
    for jpost in jcorpus["posts"]:
        post = Post()
        post.__dict__.update(**jpost)
        posts.append(post)

    del jcorpus["posts"]

    corpus = Corpus()
    corpus.__dict__.update(**jcorpus)
    corpus.posts = posts

    return corpus

def corpus_to_file(corpus, path):

    def decoder(obj):
        if isinstance(obj, np.float32):
            return float(obj)
        return obj.__dict__

    print("Saving built corpus to: "+path)
    corpus_file = open(path, mode='w')
    json.dump(corpus, corpus_file, default=decoder)
    corpus_file.close()

def remove_corpus_file(path):
    if os.path.exists(path):
        print("Removing corpus "+path)
        os.remove(path)

def main():
    """ Generate, analyze, cluster and visualize data from given subreddits """

    # Figure out what algoritms the user wants to analyze.

    parser = argparse.ArgumentParser(description='what to analyse')
    parser.add_argument('subreddit', metavar='s', type=str, nargs='*', help='which subreddits to analyze')
    parser.add_argument('-p', '--port', default=8000, type=int, help='what port to open the http visualization server on')
    parser.add_argument('-n', '--number', default=200, type=int, help='how many posts to get from every subreddit')

    parser.add_argument('-r', '--readcache', action='store_true', help='use cached files if they exist')
    parser.add_argument('-w', '--writecache', action='store_true', help='write generated data to cache files')
    parser.add_argument('-c', '--cleancache', action='store_true', help='remove previous stage caches')


    def valid_date(s):
        try:
            return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M%z")
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    parser.add_argument("-s", "--starttime", type=valid_date, required=True, help="datetime when to start collection - format YYYY-MM-DDThh:mmTZD\nex:2015-03-04T05:32+0100")
    parser.add_argument("-e", "--endtime", type=valid_date, required=True, help="datetime when to end collection - format YYYY-MM-DDThh:mmTZD\nex:2015-03-04T05:32+0100")

    parser.add_argument('-tt', '--tsne_timespan', default=250, type=float, help='How many days the timespan covers')
    parser.add_argument('-ts', '--tsne_steps', default=200, type=int, help='How many steps the data is divided into')
    parser.add_argument('-te', '--tsne_epochs', default=2000, type=int, help='How many epochs are spent to reduce the data')
    parser.add_argument('-tp', '--tsne_perplexity', default=40, type=int, help='t-sne perplexity - reduce or increase if numbers become invalid')

    args = parser.parse_args()

    subreddits = args.subreddit
    # If no subreddits, use /r/worldnews as default
    if len(subreddits) == 0:
        subreddits.append("worldnews")

    server_port = args.port
    posts = args.number

    starttime = args.starttime
    endtime = args.endtime

    read_from_cache = args.readcache
    save_to_cache = args.writecache
    remove_previous_stage_caches = args.cleancache

    reddit, pushshift_api = prc.make_reddit_instance()

    corpuses = {}
    for subreddit in subreddits:
        cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "caches")
        built_path = os.path.join(cache_path, subreddit+"_1built_"+str(posts)+".json")
        analyzed_path = os.path.join(cache_path, subreddit+"_2analyzed_"+str(posts)+".json")
        reduced_path = os.path.join(cache_path, subreddit+"_3reduced_"+str(posts)+".json")

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

                    time_start = int(starttime.timestamp())
                    time_stop = int(endtime.timestamp())
                    corpus.build(reddit, pushshift_api, time_start, time_stop, posts)

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
            corpus.reduce_data_dimensions(args.tsne_timespan, args.tsne_steps, args.tsne_epochs, args.tsne_perplexity)

            if save_to_cache:
                corpus_to_file(corpus, reduced_path)

            if remove_previous_stage_caches:
                remove_corpus_file(built_path)
                remove_corpus_file(analyzed_path)

        corpuses[subreddit] = corpus

    start_server(server_port)


if __name__ == "__main__":
    main()
