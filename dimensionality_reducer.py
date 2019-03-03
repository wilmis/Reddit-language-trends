import numpy as np
from importlib import util
import sys
import bisect

import os

theano_spec = util.find_spec("theano")
theano_found = theano_spec is not None

if theano_found:
    print("Theano found. Importing thesne...")
    
    os.environ["THEANO_FLAGS"] = "device=cuda0,floatX=float32"
    sys.path.append("thesne/model") # Does this have to be done every time the program is ran?
    from thesne.model.dynamic_tsne import dynamic_tsne
    from thesne.examples import plot
    
    print("thesne imported.")

else:
    print("Theano not found.")

    
def Dynamic_tSNE_reduce_dimensions(corpus, timespan, steps):
    # Sanity checks
    assert theano_found, \
        "Cannot use Dynamic t-SNE without Theano library."
    assert (len(corpus.posts) != 0), \
        "No posts in the corpus"

    min_time = corpus.posts[0].time
    max_time = corpus.posts[-1].time
    step_size = (max_time - timespan) / steps
    
    times = [post.time for post in corpus.posts]
    
    Xs = []
    IDs = []
    for tmin in np.arange(min_time, max_time - timespan, step_size):
        tmax = tmin + timespan
        left = bisect.bisect_right(times, tmin)
        right = bisect.bisect_left(times, tmax)
        
        x = []
        ids = []
        for post in corpus.posts[left:right]:
            x.append(list(post.analyzed_data.values()))
            ids.append(post.id)
        
        print(str(len(x))+"   "+str(tmin)+"  ->  "+str(tmax))
        Xs.append(np.array(x))
        IDs.append(ids)
    
    Ys = dynamic_tsne(Xs, IDs, perplexity=50, n_epochs=2500, initial_lr=200, final_lr=80, lmbda=0.1, verbose=1, sigma_iters=60,
                      initial_momentum = 0.4)

    #for Y in Ys:
    #    plot.plot(Y)
    
    for t in range(len(Ys)):
        for i in range(len(Ys[t])):
            post = next((p for p in corpus.posts if p.id == IDs[t][i]), None)
            post.reduced_data = tuple(Ys[t][i])


def generate_fake_data(n, dt):
    """n is number of posts, dt is number of days, dims is dimentionality"""
    import random
    from language_analyser import Post
    from language_analyser import Corpus

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
