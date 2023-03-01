import os
import sys
import marshal
import itertools
import argparse
from operator import itemgetter
from functools import partial
from collections import Counter

try:
    import cPickle as pickle
except:
    import pickle

termchar = 17 # you can assume the byte 17 does not appear in the input file

codes = dict() #codes for the symbols of the huffman tree

#needed to create the huffman encoded tree which will be used as the decoderRing
class Nodes: 
    def __init__(self, prob, sym, l = None, r = None):
        
        #probability of the symbol
        self.prob = prob

        #the symbol
        self.symbol = sym

        #left node
        self.l = l
        
        #right node
        self.r = r

        #direction (0 = left, 1 = right)
        self.code = ''

def Prob(msg):
    #helper function will calculate the probability of each letter in the message

    probability = dict()
    
    for i in msg:
        if probability.get(i) == None:
            probability[i] = 1
        else:
            probability[i] += 1
    
    return probability

def Codes(node, val = ''):
    #another helper function that gives us the codes of traveling the huffman tree ie (A: '010')

    new_value = val + str(node.code)

    if(node.l):
        Codes(node.l, new_value)
    if(node.r):
        Codes(node.r, new_value)

    if(not node.r and not node.l):
        codes[node.symbol] = new_value

    return codes

def Output(msg, coding):
    #this will give us the string output of whatever our message is
    output = []
    for i in msg:
        output.append(coding[i])

    string = ''.join([item for item in output])
    return string

def ibwt_help(msg):
    #helper function for ibwt that will assist with decompressing our message using a dictionary and list
    visited = dict()
    ranks = []
    for i in msg:
        i = str(i)
        if i in visited:
            newVal = visited[i] + 1
            ranks.append(((int(i)), newVal))
            visited.update({i: newVal})
        else:
            visited.update({i: 1})
            ranks.append((int(i), 1))

    return ranks


# This takes a sequence of bytes over which you can iterate, msg, 
# and returns a tuple (enc,\ ring) in which enc is the ASCII representation of the 
# Huffman-encoded message (e.g. "1001011") and ring is your ``decoder ring'' needed 
# to decompress that message.
def encode(msg):    
    symbol_prob = Prob(msg)                 #gets the probability of each letter
    symbols = symbol_prob.keys()            #give us each character

    #print("symbols: ", symbols)
    #print("probabilities", probabilities)

    nodes = []

    for i in symbols:
        nodes.append(Nodes(symbol_prob.get(i), i)) #adding the character and its probability to the tree

    while len(nodes) > 1:
        #creation of our huffman encoded tree

        nodes = sorted(nodes, key=lambda x: x.prob)

        right = nodes[0]
        left = nodes[1]

        left.code = 0
        right.code = 1

        newNode = Nodes(left.prob + right.prob, left.symbol + right.symbol, left, right)

        nodes.remove(left)
        nodes.remove(right)
        nodes.append(newNode)

    huff_enc = Codes(nodes[0])    #passing the head of our tree which will give us all the codes for each character
    #print(huffman_encode)

    encode_output = Output(msg, huff_enc) #taking our message and converting it into a binary string using our codes
    #print("Encoded Output: ", encode_output)

    return encode_output, nodes[0]  #returning our encode_output and the head of our tree, which will be our decoderRing


# This takes a string, cmsg, which must contain only 0s and 1s, and your  
# representation of the ``decoder ring'' ring, and returns a bytearray msg which 
# is the decompressed message. 
def decode(cmsg, decoderRing):
    # Creates an array with the appropriate type so that the message can be decoded.
    byteMsg = bytearray()

    head = decoderRing  #storing the tree since we're going to be traversing it

    #traversing the tree to get our characters back
    for i in cmsg:
        if i == '1':
            decoderRing = decoderRing.r
        elif i == '0':
            decoderRing = decoderRing.l
        try:
            if decoderRing.l.symbol == None and decoderRing.r.symbol == None:
                pass
        except AttributeError:
            byteMsg.append(decoderRing.symbol)
            decoderRing = head
    
    return byteMsg



# This takes a sequence of bytes over which you can iterate, msg, and returns a tuple (compressed, ring) 
# in which compressed is a bytearray (containing the Huffman-coded message in binary, 
# and ring is again the ``decoder ring'' needed to decompress the message.
def compress(msg, useBWT):
    #we want to use bwt and/or mtf first, then encode the message, then compress it using a bytearray

    if useBWT:
        msg = bwt(msg)
        msg = mtf(msg)

    # Initializes an array to hold the compressed message.
    val = 0x0   #val will be used to get bytes to add to out byte array
    counter = 0     #keeping count of bytes (8bits)

    msg, decoderRing = encode(msg) 

    compressed = bytearray()

    #compressing our msg using a bit manipulation and appending every 8 bits into the byte array
    for i in msg:
        if i == '0':
            val = val << 1
        elif i == '1':
            val = val << 1 | 0x01

        counter += 1

        if (counter % 8 == 0):
            compressed.append(val)
            val = 0x0
        
        if (counter == len(msg)):
            compressed.append(val)
            compressed.append(counter % 8) #we want to just append the final bits even if less than 8, and also append something that tells us how many bytes it truly is
                                                #as ('010' and '10' would both be just read as 2)

    return compressed, decoderRing

# This takes a sequence of bytes over which you can iterate containing the Huffman-coded message, and the 
# decoder ring needed to decompress it.  It returns the bytearray which is the decompressed message. 
def decompress(msg, decoderRing, useBWT):
    # We have to go in reverse order of compress, which means we have to turn our bytearray into bitstrings, then decode, then do ibwt and/or imtf
    # Creates an array with the appropriate type so that the message can be decoded.
    byteArray = bytearray(msg)

    decompressedMsg = ''

    # Turning our bytearray into a bitstring
    for i in range(len(byteArray)):
        
        if (i+2) == len(byteArray):     #this is when we're near the end and have to find out how many bits our last byte truly is
            decompressedMsg += str((format(byteArray[i], "0{}b".format(byteArray[i+1]))))
            break
        else:
            decompressedMsg += str((format(byteArray[i], '08b')))   #reverting bytes back into bits

    #decode the message
    decompressedMsg = decode(decompressedMsg, decoderRing)

    # before you return, you must invert the move-to-front and BWT if applicable
    # here, decompressed message should be the return value from decode()
    if useBWT:
        decompressedMsg = imtf(decompressedMsg)
        decompressedMsg = ibwt(decompressedMsg)

    return decompressedMsg

# memory efficient iBWT
def ibwt(msg):
    # using our helper function to invert BWT
    ranked_msg = ibwt_help(msg)
    ranked_msg_sorted = sorted(ranked_msg)
    index = ranked_msg.index((termchar, 1))
    inverted = bytearray()

    for i in range(len(ranked_msg)):    #this does most of the hard work of the ibwt
        tup = ranked_msg_sorted[index]
        index = ranked_msg.index(tup)
        inverted.append(tup[0])

    return inverted


# Burrows-Wheeler Transform fncs
def radix_sort(values, key, step=0):
    sortedvals = []
    radix_stack = []
    radix_stack.append((values, key, step))

    while len(radix_stack) > 0:
        values, key, step = radix_stack.pop()
        if len(values) < 2:
            for value in values:
                sortedvals.append(value)
            continue

        bins = {}
        for value in values:
            bins.setdefault(key(value, step), []).append(value)

        for k in sorted(bins.keys()):
            radix_stack.append((bins[k], key, step + 1))
    return sortedvals
            
# memory efficient BWT
def bwt(msg):
    def bw_key(text, value, step):
        return text[(value + step) % len(text)]

    msg = msg + termchar.to_bytes(1, byteorder='big')

    bwtM = bytearray()

    rs = radix_sort(range(len(msg)), partial(bw_key, msg))
    for i in rs:
        bwtM.append(msg[i - 1])

    return bwtM[::-1]

# move-to-front encoding fncs
def mtf(msg):
    # Initialise the list of characters (i.e. the dictionary)
    dictionary = bytearray(range(256))
    
    # Transformation
    compressed_text = bytearray()
    rank = 0

    # read in each character
    for c in msg:
        rank = dictionary.index(c) # find the rank of the character in the dictionary
        compressed_text.append(rank) # update the encoded text
        
        # update the dictionary
        dictionary.pop(rank)
        dictionary.insert(0, c)

    #dictionary.sort() # sort dictionary
    return compressed_text # Return the encoded text as well as the dictionary

# inverse move-to-front
def imtf(compressed_msg):
    compressed_text = compressed_msg
    dictionary = bytearray(range(256))

    decompressed_img = bytearray()

    # read in each character of the encoded text
    for i in compressed_text:
        # read the rank of the character from dictionary
        decompressed_img.append(dictionary[i])
        
        # update dictionary
        e = dictionary.pop(i)
        dictionary.insert(0, e)
        
    return decompressed_img # Return original string

if __name__=='__main__':

    # argparse is an excellent library for parsing arguments to a python program
    parser = argparse.ArgumentParser(description='<Insert a cool name for your compression algorithm> compresses '
                                                 'binary and plain text files using the Burrows-Wheeler transform, '
                                                 'move-to-front coding, and Huffman coding.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', action='store_true', help='Compresses a stream of bytes (e.g. file) into a bytes.')
    group.add_argument('-d', action='store_true', help='Decompresses a compressed file back into the original input')
    group.add_argument('-v', action='store_true', help='Encodes a stream of bytes (e.g. file) into a binary string'
                                                       ' using Huffman encoding.')
    group.add_argument('-w', action='store_true', help='Decodes a Huffman encoded binary string into bytes.')
    parser.add_argument('-i', '--input', help='Input file path', required=True)
    parser.add_argument('-o', '--output', help='Output file path', required=True)
    parser.add_argument('-b', '--binary', help='Use this option if the file is binary and therefore '
                                               'do not want to use the BWT.', action='store_true')

    args = parser.parse_args()

    compressing = args.c
    decompressing = args.d
    encoding = args.v
    decoding = args.w


    infile = args.input
    outfile = args.output
    useBWT = not args.binary

    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        sinput = fp.read()
        fp.close()
        if compressing:
            msg, tree = compress(sinput,useBWT)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
        else:
            msg, tree = encode(sinput)
            print(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pck, msg = marshal.load(fp)
        tree = pickle.loads(pck)
        fp.close()
        if decompressing:
            sinput = decompress(msg, tree, useBWT)
        else:
            sinput = decode(msg, tree)
            print(sinput)
        fp = open(outfile, 'wb')
        fp.write(sinput)
        fp.close()