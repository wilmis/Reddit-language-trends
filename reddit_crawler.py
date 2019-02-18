#!/usr/bin/env python3

import praw


# TODO Skapa reddit användare. Registrera botten och lägg in alla id, användarnamn och lösenord.
"Create an authorized reddit instance. "
reddit = praw.Reddit(client_id='my client id',
                     client_secret='my client secret',
                     user_agent='my user agent',
                     username='my username',
                     password='my password')

print(reddit.read_only)  # Output: False


"Obtain a subreddit instance"
# assume you have a Reddit instance bound to variable `reddit`
subreddit = reddit.subreddit('redditdev')

print(subreddit.display_name)  # Output: redditdev
print(subreddit.title)         # Output: reddit Development
print(subreddit.description)   # Output: A subreddit for discussion of ...


"Obtain submission instance form a subreddit."
"""Sorts that can be itteradet through:
controversial
gilded
hot
new
rising
top

Returns a listgenerator."""
# assume you have a Subreddit instance bound to variable `subreddit`
for submission in subreddit.hot(limit=10):
    print(submission.title)  # Output: the submission's title
    print(submission.score)  # Output: the submission's score
    print(submission.id)     # Output: the submission's ID
    print(submission.url)    # Output: the URL the submission points to
                             # or the submission's URL if it's a self post


"""Obtain comment instances."""
top_level_comments = list(submission.comments)
all_comments = submission.comments.list()
