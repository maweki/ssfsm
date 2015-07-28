def all_words(alphabet, upto):
    from itertools import product
    for length in range(upto + 1):
        for word in product(alphabet, repeat=length):
            yield word
