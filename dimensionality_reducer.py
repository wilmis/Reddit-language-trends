import abc
import numpy as np
from importlib import util
import sys

from language_analyser import Post
from language_analyser import Corpus

theano_spec = util.find_spec("theano")
theano_found = theano_spec is not None

if theano_found:
    print("Theano found. Importing thesne...")
    sys.path.append("thesne/model") # Does this have to be done every time the program is ran?
    import thesne.model.dynamic_tsne

else:
    print("Theano not found.")


class Dim_Reducer(abc.ABC):
    def __init__(self, corpus):
        self.corpus = corpus

    @abc.abstractmethod
    def start_processing(self, callback):
        pass

    @abc.abstractmethod
    def stop_processing(self):
        pass

    @abc.abstractmethod
    def get_progress(self):
        pass


class Dim_Reducer_Dynamic_tSNE(Dim_Reducer):
    def __init__(self, corpus):
        super().__init__(corpus)

        # Sanity checks
        assert theano_found, \
            "Cannot use Dynamic t-SNE without Theano library."
        assert (len(corpus.posts) != 0), \
            "No posts in the corpus"

        # How many data-points/dimensions the posts have?
        self.Xdims = len(np.concatenate(list(corpus.posts[0].analyzed_data.values())))
        print(self.Xdims)

    def start_processing(self, callback):
        pass

    def stop_processing(self):
        pass

    def get_progress(self):
        pass


class Dim_Reducer_Client(Dim_Reducer):
    def __init__(self, corpus, address, port):
        super().__init__(corpus)
        self.address = address
        self.port = port

    def start_processing(self, callback):
        pass

    def stop_processing(self):
        pass

    def get_progress(self):
        pass


def generate_fake_data(n, dt):
    """n is number of posts, dt is number of days, dims is dimentionality"""
    import random

    c = Corpus("FakeData")

    for i in range(n):
        p = Post(["This", "is", "a", "fake", "post"], random.random() * dt, "axelwickm", False,
                 "https://www.reddit.com/r/CasualConversation/comments/95hpj2/today_i_learned_that_you_eat_popcorn_microwaved/")
        p.analyzed_data = {
            "a": [random.random() * 3, 2, random.random() * 0.2],
            "b": [p.time / dt * 3],
            "c": [3 * p.time / dt * p.time / dt * p.time / dt - 0.5 * p.time / dt * p.time / dt - p.time / dt + 2]
        }

        c.add_post(p)

    return c


if __name__ == "__main__":
    corpus = generate_fake_data(200, 300)
    analyzer = Dim_Reducer_Dynamic_tSNE(corpus)

    def done():
        print("Done with processing!")

    analyzer.start_processing(done)
