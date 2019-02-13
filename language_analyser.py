#!/usr/bin/env python3

import reddit_crawler

import argparse

def main(subreddits):
    print(subreddits)

if __name__ == "__main__":
    # Figure out what algoritms the user wants to analyze. 
    # This is fed into the program by typing for example:
    # python language_analyzer.py aww me_irl
    parser = argparse.ArgumentParser(description="What to analyse")
    parser.add_argument('subreddit', metavar="s", type=str, nargs='*',
        help='What subreddits to analyze')
    args = parser.parse_args()
    subreddits = args.subreddit
    # If no subreddits 
    if len(subreddits) == 0:
        subreddits.append("sweden")

    main(subreddits)