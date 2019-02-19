#!/usr/bin/env python3

import praw

def make_reddit_instance():
    # TODO Skapa reddit användare. Registrera botten och gör så alla id inte är hårdkodade.
    "Create an authorized reddit instance. "
    reddit = praw.Reddit(client_id=,
                         client_secret=,
                         user_agent='languageBot1',
                         username='languageTechbot',
                         password=)

    print(reddit.read_only)  # Output: False
    return reddit


def enter_subreddit(reddit):
    """Obtain a subreddit instance"""
    # assume you have a Reddit instance bound to variable `reddit`
    subreddit = reddit.subreddit('sweden')

    print(subreddit.display_name)  # Output: redditdev
    print(subreddit.title)         # Output: reddit Development
    #print(subreddit.description)   # Output: A subreddit for discussion of ...
    return subreddit




def in_subreddit(subreddit):
    """Obtain submission instance form a subreddit.
    Sorts that can be itteradet through:
    controversial
    gilded
    hot
    new
    rising
    top

    Returns a listgenerator."""
    # assume you have a Subreddit instance bound to variable `subreddit`
    # limit=None ger så många som möjligt
    for submission in subreddit.hot(limit=3):
        print("New post: ")
        print(submission.title)  # Output: the submission's title
        print("1_____")
        print(submission.score)  # Output: the submission's score
        print("2____")
        print(submission.id)     # Output: the submission's ID
        print("3______")
        print(submission.url)    # Output: the URL the submission points to
                                 # or the submission's URL if it's a self post
        print("4_______")
        #Obtain comment instances.
        top_level_comments = list(submission.comments)
        #print(top_level_comments)
        print("comments---------------------------")
        all_comments = submission.comments.list()
        for comment in all_comments:
            print(comment.body)
        #print(all_comments)





def __main__():
    reddit = make_reddit_instance()
    subreddit=enter_subreddit(reddit)
    in_subreddit(subreddit)


if __name__ == "__main__":
    __main__()
