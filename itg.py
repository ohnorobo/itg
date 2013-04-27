#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pprint

INPUT_FILE = "sentences.in"
OUTPUT_FILE = "sentences.out"
PROBS_FILE = "probs.dict"
probs = {}

#log probabilities
AB = -1   # A -> [AA]
BA = -2   # A -> ⟨AA⟩
WE = -20  # A -> word.in / ϵ
EW = -21  # A -> ϵ / word.out

WW = -1000 # A -> word.in / word.out
          # if there is no entry for the pair in PROBS_FILE

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

    def __init__(self, w_in, w_out, prob):
        """
        Args:
            w_in - string, input word
            w_out - string, output word
            prob - float
        """
        self.w_in = w_in
        self.w_out = w_out
        self.prob = prob

    def __str__(self):
        return str(self.w_in) + '/' + str(self.w_out)

    def get_alignments(self):
        return [(self.w_in, self.w_out)]

    __repr__ = __str__

###############



def read_probs(filename):
    global probs
    p = file(filename, 'r')

    for line in p:
        w_in, w_out, prob = line.split()
        #print w_in, w_out, float(prob)
        probs[(w_in, w_out)] = float(prob)


def align(st_in, st_out):
    print st_in, st_out

    s_in = st_in.split()
    s_out = st_out.split()

    parse = prob_align(s_in, 0, len(s_in), s_out, 0, len(s_out), 0)

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






def prob_align(s_in, i, k, s_out, u, w, depth):
    """
    Args:
        s_in - list of strings, input sentence
        s_out - list of strings, output sentence
        i, k - ints, input start and end index
        u, w - ints, output start and end index

    Return:
        returns a Parse, wth the most probable alignment for these indicies
    """

    #print "aligning", s_in[i:k], " : ", s_out[u:w]
    #print " "*depth, "a", i, k, ":", u, w


    ##Base Cases
    #word / ϵ
    if i == k: # is w-u == 1 ?
        word_out = s_out[u:w]
        #print 'ϵ', word_out
        return Leaf('ϵ', word_out, EW*len(word_out))

    #ϵ / word
    if u == w: # is k-1 == 1 ?
        word_in = s_in[i:k]
        #print word_in, 'ϵ'
        return Leaf(word_in, 'ϵ', WE*len(word_in))

    #word / word
    if k-i == 1 and w-u == 1:
        word_in = s_in[i:k][0]
        word_out = s_out[u:w][0]
        #print word_in, word_out
        return Leaf(word_in, word_out, word_alignment_prob(word_in, word_out))

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
                    left = prob_align(s_in, i, j, s_out, u, v, depth+1)
                    right = prob_align(s_in, j, k, s_out, v, w, depth+1)
                    parse = Node(left,
                                 right,
                                 left.prob+right.prob+AB,
                                 False)
                    parses.append(parse)

                    #inverted
                    left_inv = prob_align(s_in, i, j, s_out, v, w, depth+1)
                    right_inv = prob_align(s_in, j, k, s_out, u, v, depth+1)
                    parse_inv = Node(left_inv,
                                     right_inv,
                                     left_inv.prob+right_inv.prob+BA,
                                     True)
                    parses.append(parse_inv)

                #pprint( parses )

        return max(parses, key=lambda x: x.prob)


prob_align = Memoize(prob_align)


def word_alignment_prob(word_in, word_out):
    global probs

    pair = (word_in, word_out)
    if pair in probs:
        return probs[pair]
    else:
        return WW






#####

if __name__ == "__main__": #i.e. run directly
    read_probs(PROBS_FILE)
    all_in = file(INPUT_FILE, 'r')
    all_out = file(OUTPUT_FILE, 'r')

    for in_sentence, out_sentence in zip(all_in, all_out):
        align(in_sentence, out_sentence)

