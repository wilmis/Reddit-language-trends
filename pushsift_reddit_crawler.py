#!/usr/bin/env python3

import pprint
import praw
from praw.models import MoreComments
import time
import re
from psaw import PushshiftAPI

import json
import datetime as dt
import language_analyser as la
import os

#from datetime import datetime

# skapa funktion för att bestämma vilket tidsspann som ska sökas över

# plocka hem id på de submissions som förkommer mellan det tidsspannet

# skicka de till reddit_crawler för att plockain data.


#TODO yield list with tokenised sentences. Checking stop tokens.
def tokens(source):
    return_list=[[]]
    stopWords=['.','?','!']
    regex = r"--|(?:Mr|St|Mrs|Dr)\.|\w+(?:['-]\w+)*|\S"
    for token in re.findall(regex, source):
        return_list[-1].append(token)
        if token in stopWords:
            return_list.append([])

    if return_list[-1] == []:
        del return_list[-1]

    if return_list == []:
        print("WRONG:")
        print(repr(source))

    return return_list



def make_reddit_instance():
    # TODO Skapa reddit användare. Registrera botten och gör så alla id inte är hårdkodade.
    "Create an authorized reddit instance. "
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "LOGIN.json")) as f:
        data = json.load(f)

    reddit = praw.Reddit(client_id=data["client_id"],
                         client_secret=data["client_secret"],
                         user_agent=data["user_agent"],
                         username=data["username"],
                         password=data["password"])


    list_of_submissions = make_pushshiftAPI(reddit)
    #print(reddit.read_only)  # Output: False
    return (reddit, make_pushshiftAPI(reddit))

def make_pushshiftAPI(reddit):
    api = PushshiftAPI(reddit)
    return api

def query(reddit, api, start_epoch, subreddit, limit_sub):
    # subreddit är där vi plockar submissions ifrån
    # limit är antal
    gen = list(api.search_submissions(before=start_epoch, subreddit=subreddit, limit=limit_sub))
    list_of_submissions = list(gen)
    posts = in_subreddit(reddit, list_of_submissions)
    return posts

def enter_subreddit(reddit, subreddit):
    """Obtain a subreddit instance"""
    # assume you have a Reddit instance bound to variable `reddit`
    subreddit = reddit.subreddit(subreddit)

    #print(subreddit.display_name)  # Output: redditdev
    #print(subreddit.title)         # Output: reddit Development
    #print(subreddit.description)   # Output: A subreddit for discussion of ...
    return subreddit


def in_subreddit(reddit, submissions):
    """Obtain submission instance form a subreddit.
    Sorts that can be iterated through:
    controversial
    gilded
    hot
    new
    rising
    top

    Returns a listgenerator."""
    # assume you have a Subreddit instance bound to variable `subreddit`
    # limit=None ger så många som möjligt
    # (tokens, time, user, is_comment, url)
    list_to_return = []
    for submission_id in submissions:
        submission = reddit.submission(id=submission_id)

        sub = {"title" :[], "selftext":[], "time":[],  "comments":[], "url":[]}

        for word in tokens(submission.title):
            sub["title"].append(word)
        #print(submission.title)  # Output: the submission's title

        if submission.is_self:
            for word in tokens(submission.selftext):
                sub["selftext"].append(word)

        # FIXME: replace_more slows down the script ALOT, top comments instead

        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            sub["comments"].append(tokens(str(comment.body)))

        sub["time"]= submission.created_utc # tid när subbmission skapades
        sub["url"] = submission.url   # Output: the URL the submission points to
        #pprint.pprint(vars(submission))
        title_selftext = la.Post(tokens=sub["title"] + sub["selftext"], time=sub["time"], user="Unavailible", is_comment=False, parentPost=None, url=sub["url"])
        #print(sub["title"])
        postList = []

        for comment in submission.comments.list():
            tokenised = tokens(str(comment.body))
            postList.append(la.Post(tokens=comment, time=sub["time"],
                               user="Unavailible", is_comment=True, parentPost=title_selftext,url=sub["url"]))
        yield (title_selftext, postList)

        #print(datetime.fromtimestamp(title_selftext.time))
        #list_to_return.append((title_selftext, postList))
    #return list_to_return



def __main__():
    reddit_and_subs = make_reddit_instance()
    #return in_subreddit(reddit_and_subs)
    #for x in in_subreddit(reddit_and_subs):
        #print(x[0].tokens)



if __name__ == "__main__":
    __main__()
