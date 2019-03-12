# Reddit-language-trends

This project analyzes language uses trends for one or multiple subreddits over time.

![Preview](https://raw.githubusercontent.com/wilmis/Reddit-language-trends/master/example.png)


The language_analyzer.py (Python 3.7) script collects, analyzes, reduces, then visualizes posts from a given subreddit, and stores them in .json file (which are not included here). Reddit API credentials will also have to be added to the LOGIN.json file.

Example usage:
```
python language_analyser.py me_irl -n 2000 -s 2015-10-01T00:00+0000 -e 2016-10-01T00:00+0000 -rw
```


To visualize existing .json file caches, simply run the start_server.py, which will open the visualization in the default web browser.
A dimensionality reduction algorithm (Dynamic t-SNE) is used to represent how features of posts change over time. To run this, Theano needs to be installed. 
