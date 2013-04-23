#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pprint

ENGLISH_FILE = "test.en"
GERMAN_FILE = "test.de"
PROBS_FILE = "itg.dict"
probs = {}

#log probabilities
AB = -1   # A -> [AA]
BA = -2   # A -> ⟨AA⟩
WE = -20  # A -> word.en / ϵ
EW = -21  # A -> ϵ / word.de

WW = -1000 # A -> word.en / word.de
          # if there is no entry for the pair in PROBS_FILE

#import sys
#sys.setrecursionlimit(20)


#############Memoization
#http://stackoverflow.com/questions/1988804/what-is-memoization-and-how-can-i-use-it-in-python

class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}
    def __call__(self, *args):
        targs = args[1], args[2], args[4], args[5]
        #print targs
        if not targs in self.memo:
            self.memo[targs] = self.f(*args)
        return self.memo[targs]


#############Representation of Parse Trees

class Parse():
    pass

class Node(Parse):

    def __init__(self, left, right, prob, inverted):
        """
        Args:
            left - Parse
            right - Parse
            prob - float
            inverted -  boolean, is this parse inverted in the target?
        """
        self.left = left
        self.right = right
        self.prob = prob
        self.inverted = inverted

    def __str__(self):
        if self.inverted:
            return ' ⟨' + str(self.left) + ',' + str(self.right) + '⟩ '
        else:
            return ' [' + str(self.left) + ',' + str(self.right) + '] '

    def get_alignments(self):
        a = self.left.get_alignments()
        a.extend(self.right.get_alignments())
        return a

    __repr__ = __str__

class Leaf(Parse):

    def __init__(self, en, de, prob):
        """
        Args:
            en - string, english word
            de - string, german word
            prob - float
        """
        self.en = en
        self.de = de
        self.prob = prob

    def __str__(self):
        return str(self.en) + '/' + str(self.de)

    def get_alignments(self):
        return [(self.en, self.de)]

    __repr__ = __str__

###############



def read_probs(filename):
    global probs
    p = file(filename, 'r')

    for line in p:
        english, german, prob = line.split()
        #print english, german, float(prob)
        probs[(english, german)] = float(prob)


def align(english, german):
    print english, german

    en = english.split()
    de = german.split()

    parse = prob_align(en, 0, len(en), de, 0, len(de), 0)

    print parse
    #print parse.prob
    alignment = parse.get_alignments()
    #print " "
    print_alignment(alignment)
    prob_align.memo = {} #reset memoization
    #print "==="

def print_alignment(alignment):
    for pair in alignment:
        if isinstance(pair[0], list):
            for a in pair[0]:
                print a, pair[1]
        elif isinstance(pair[1], list):
            for a in pair[1]:
                print pair[0], a
        else:
            print pair[0], pair[1]






def prob_align(en, i, k, de, u, w, depth):
    """
    Args:
        en - list of strings, english sentence
        de - list of strings, german sentence
        i, k - ints, english start and end index
        u, w - ints, german start and end index

    Return:
        returns a Parse, wth the most probable alignment for these indicies
    """

    #print "aligning", en[i:k], " : ", de[u:w]
    #print " "*depth, "a", i, k, ":", u, w


    ##Base Cases
    #word / ϵ
    if i == k: # is w-u == 1 ?
        word_de = de[u:w]
        #print 'ϵ', word_de
        return Leaf('ϵ', word_de, EW*len(word_de))

    #ϵ / word
    if u == w: # is k-1 == 1 ?
        word_en = en[i:k]
        #print word_en, 'ϵ'
        return Leaf(word_en, 'ϵ', WE*len(word_en))

    #word / word
    if k-i == 1 and w-u == 1:
        word_en = en[i:k][0]
        word_de = de[u:w][0]
        #print word_en, word_de
        return Leaf(word_en, word_de, word_alignment_prob(word_en, word_de))

    ##Recursive Case
    else:
        parses = []

        for j in xrange(i, k):
            for v in xrange(u, w):
                if j==i and v==u:
                    pass
                elif j==k and v==w:
                    pass
                else:

                    #aligned
                    left = prob_align(en, i, j, de, u, v, depth+1)
                    right = prob_align(en, j, k, de, v, w, depth+1)
                    parse = Node(left,
                                 right,
                                 left.prob+right.prob+AB,
                                 False)
                    parses.append(parse)

                    #inverted
                    left_inv = prob_align(en, i, j, de, v, w, depth+1)
                    right_inv = prob_align(en, j, k, de, u, v, depth+1)
                    parse_inv = Node(left_inv,
                                     right_inv,
                                     left_inv.prob+right_inv.prob+BA,
                                     True)
                    parses.append(parse_inv)

                #pprint( parses )

        return max(parses, key=lambda x: x.prob)


prob_align = Memoize(prob_align)


def word_alignment_prob(word_en, word_de):
    global probs

    pair = (word_en, word_de)
    if pair in probs:
        return probs[pair]
    else:
        return WW






#####

if __name__ == "__main__": #i.e. run directly
    read_probs(PROBS_FILE)
    en = file(ENGLISH_FILE, 'r')
    de = file(GERMAN_FILE, 'r')

    for en_sentence, de_sentence in zip(en, de):
        align(en_sentence, de_sentence)

