#!/usr/bin/env python3

import pprint
import praw
from praw.models import MoreComments
import time
import json
import re


def tokens(source):
    regex = r"--|(?:Mr|St|Mrs|Dr)\.|\w+(?:['-]\w+)*|\S"
    for line in source:
        for token in re.findall(regex, line):
            yield token

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
    
    reddit = praw.Reddit(client_id='Xt0iuspmVUn8GQ',
                         client_secret=,
                         user_agent='languageBot1',
                         username='languageTechbot',
                         password=)

    #print(reddit.read_only)  # Output: False
    return reddit


def enter_subreddit(reddit, subreddit):
    """Obtain a subreddit instance"""
    # assume you have a Reddit instance bound to variable `reddit`
    subreddit = reddit.subreddit(subreddit)

    #print(subreddit.display_name)  # Output: redditdev
    #print(subreddit.title)         # Output: reddit Development
    #print(subreddit.description)   # Output: A subreddit for discussion of ...
    return subreddit




def in_subreddit(subreddit):
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
    for submission in subreddit.hot(limit=None):
        sub = {"title" :[], "selftext":[], "time":[], "comments":[], "url":[]}
        temp_list=[]
        temp_list.append(submission.title)
        for word in tokens(temp_list):
            sub["title"].append(word)
        #print(submission.title)  # Output: the submission's title
        temp_list.clear()
        temp_list.append(submission.selftext)
        for word in tokens(temp_list):
            sub["selftext"].append(word)
        submission.comments.replace_more(limit=None)
        temp_list.clear()
        for comment in submission.comments.list():
            temp_list.append(comment.body)
        for comment in tokens(temp_list):
            sub["comments"].append(comment)
        sub["time"]= submission.created_utc # tid när subbmission skapades
        sub["url"] = submission.url   # Output: the URL the submission points to
        #pprint.pprint(vars(submission))
        title_selftext = Post(tokens=sub["title"] + sub["selftext"], time=sub["time"], user="Unavailible", is_comment=False, url=sub["url"])
        comments = Post(tokens=sub["comments"], time=sub["time"], user="Unavailible", is_comment=False, url=sub["url"])
        return (title_selftext, comments)

from language_analyser import Post

def __main__():
    reddit = make_reddit_instance()
    subreddit=enter_subreddit(reddit,"news")
    return in_subreddit(subreddit)


if __name__ == "__main__":
    __main__()
