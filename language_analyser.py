#!/usr/bin/env python3

import pushsift_reddit_crawler as prc

import argparse
import uuid
import pickle
import os
import datetime as dt
import http.server
import webbrowser
from collections import Counter
import math

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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
                if len([1 for x in self.posts if x.id == p[0].id]) == 0: # FIXME: this is slow and ugly
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
        for post in self.posts:
            print("\r{0} %".format(int(i/len(self.posts)*90)), end="\r")
            i += 1
            ## Tuples: First index is posttitle + self text
            ##         Second index is comments
            #polarity_tuples = analyze.polarity_scores(" ".join(post.tokens))
            #print(polarity_tuples)
            sentiments = {"neg":[], "neu":[], "pos":[], "compound":[]}
            flat_sanitized = [item for sublist in post.sanitized for item in sublist]

            average_token_length = 0
            for token in flat_sanitized:
                vocabulary[token] += 1
                average_token_length += len(token)
            average_token_length /= len(flat_sanitized)

            average_sentence_length = 0
            for sentence in post.sanitized:
                average_sentence_length += len(sentence)

                polarity_text = analyze.polarity_scores(" ".join(sentence))
                for key, value in polarity_text.items():
                    sentiments[key].append(value)

            average_sentence_length /= len(post.sanitized)

            for key, value in sentiments.items():
                sentiments[key] = sum(sentiments[key]) / len(sentiments[key])
            

            post.analyzed_data = {
                "Post length" : len(flat_sanitized),
                "Average sentence length" : average_sentence_length,
                "Average token length" : average_token_length,

                "Sentiment negative" : sentiments["neg"], # Will these cause problems with t-sne because they are too similar?
                "Sentiment neutral" : sentiments["neu"],
                "Sentiment positive" : sentiments["pos"]
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

            print("\n")
            print(" ".join(flat_sanitized))
            for key, value in post.analyzed_data.items():
                print(key, ":", value)

        print("done")
                




            
        
        ## TODO: Fixa meningslängd. Remove stopwords from count
        #for tuples in self.posts:
        #    len_count = 0
        #    for text in tuples:
        #            len_count += 1
        #            sentence_length = len_count
                   
            
        #print({"Sentence :":vs, })
        ## TODO: Medelvärde av alla meningar för total sentiment av posten
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
            corpus.sort_posts()
            corpus.reduce_data_dimensions()

            if save_to_cache:
                corpus_to_file(corpus, reduced_path)

            if remove_previous_stage_caches:
                remove_corpus_file(built_path)
                remove_corpus_file(analyzed_path)



        corpuses[subreddit] = corpus

    # Open website in default browser
    print("Hosting in default webbrowser on: "+"http://localhost:"+str(server_port))
    webbrowser.open("http://localhost:"+str(server_port))

    # Open HTTP-server
    server_address = ('', server_port)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    print("Starting http server")
    httpd.serve_forever()
    

if __name__ == "__main__":
    main()
