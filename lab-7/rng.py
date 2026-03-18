import random

_rng = random.Random()


def seed(value):
    _rng.seed(value)


def random():
    return _rng.random()


def randint(a, b):
    return _rng.randint(a, b)


def choice(seq):
    return _rng.choice(seq)


def shuffle(seq):
    _rng.shuffle(seq)


def getstate():
    return _rng.getstate()


def setstate(state):
    _rng.setstate(state)
