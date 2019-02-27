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



def tokens(source):
    regex = r"--|(?:Mr|St|Mrs|Dr)\.|\w+(?:['-]\w+)*|\S"
    for line in source:
        for token in re.findall(regex, line):
            yield token

def make_reddit_instance( year, month, day, subred, limit_sub):
    # TODO Skapa reddit användare. Registrera botten och gör så alla id inte är hårdkodade.
    "Create an authorized reddit instance. "
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "LOGIN.json")) as f:
        data = json.load(f)

    reddit = praw.Reddit(client_id=data["client_id"],
                         client_secret=data["client_secret"],
                         user_agent=data["user_agent"],
                         username=data["username"],
                         password=data["password"])

    list_of_submissions = make_pushshiftAPI(reddit, year, month, day, subred, limit_sub)
    #print(reddit.read_only)  # Output: False
    return (reddit, list_of_submissions)

def make_pushshiftAPI(reddit, year, month, day, subred, limit_sub):
    api = PushshiftAPI(reddit)
    # Skriv det datum du vill plocka submissions fram till
    start_epoch=int(dt.datetime(year, month, day).timestamp())
    # subreddit är där vi plockar submissions ifrån
    # limit är antal
    gen =list(api.search_submissions(before=start_epoch,subreddit=subred,limit=limit_sub))
    list_of_submissions = list(gen)
    return list_of_submissions

def enter_subreddit(reddit, subreddit):
    """Obtain a subreddit instance"""
    # assume you have a Reddit instance bound to variable `reddit`
    subreddit = reddit.subreddit(subreddit)

    #print(subreddit.display_name)  # Output: redditdev
    #print(subreddit.title)         # Output: reddit Development
    #print(subreddit.description)   # Output: A subreddit for discussion of ...
    return subreddit


def in_subreddit(reddit_and_subs):
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
    list_to_return =[]
    for submission_id in reddit_and_subs[1]:
        submission = reddit_and_subs[0].submission(id=submission_id)
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
        title_selftext = la.Post(tokens=sub["title"] + sub["selftext"], time=sub["time"], user="Unavailible", is_comment=False, parentPost=None, url=sub["url"])
        comments = la.Post(tokens=sub["comments"], time=sub["time"],
                           user="Unavailible", is_comment=True, parentPost=title_selftext,url=sub["url"])
        #print(datetime.fromtimestamp(title_selftext.time))
        #list_to_return.append((title_selftext, comments))
    #return list_to_return
        yield (title_selftext, comments)


def __main__():
    reddit_and_subs = make_reddit_instance(2017, 1, 1, 'worldnews',10)
    #return in_subreddit(reddit_and_subs)
    #for x in in_subreddit(reddit_and_subs):
        #print(x[0].tokens)



if __name__ == "__main__":
    __main__()
