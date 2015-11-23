import sys
sys.path.append('/srv/data/web/vhosts/www.lilbluj.com/htdocs/python/pkgs')

import requests, random, re, math, nltk, json, sys, tweepy
from bs4 import BeautifulSoup
import secrets

#############################################################################
#First section - pull training set for language model from wikiquotes corpus#
#############################################################################

def buildQuoteCorpus(quoteObj):
    stemmer = nltk.stem.snowball.SnowballStemmer("english")
    quotes = []

    for author in quoteObj["Authors"].keys():
        for quote in quoteObj["Authors"][author]:
            #sentence seg doesn't know to remove the period from the last word. Let's help 'em out!
            if quote[len(quote)-1] == '.':
                quote = quote[:len(quote)-1] + " ."
            #{ } serve as starting and ending characters, respectively
            quotes.extend(nltk.word_tokenize("{ " + str(quote.lower()) + " }"))
    for loc in range(len(quotes)):
        quotes[loc] = stemmer.stem(quotes[loc])
        if loc % 50000 == 0:
            sys.stdout.write(str(loc) + " ")
        
    return quotes

def buildQuoteFreq(quoteObj):
    quoteCorpus = buildQuoteCorpus(quoteObj)

    tgs = nltk.trigrams(quoteCorpus)
    tgsFreq = nltk.FreqDist(tgs)
    return nltk.KneserNeyProbDist(tgsFreq)

#############################################################################
#          Second section - source random book from Project Gutenberg       #
#############################################################################

def getBook(book = -1):
        
    BASE_URL = "http://www.gutenberg.org/files/"
    MAX_BOOKS = 49132 #based on http://www.gutenberg.org/dirs/GUTINDEX.ALL. Subject to updates.
    maxAttempts = 3 

    #some (small percentage) of gutenberg files are audiobooks, unused, etc
    #loop repeats x times until good text source is found
    while maxAttempts > 0:
        bookNum = random.randint(1, MAX_BOOKS)
        if book != -1:
            bookNum = book
        print bookNum
        print BASE_URL + str(bookNum)

        body = requests.get(BASE_URL + str(bookNum)).text
        soup = BeautifulSoup(body)
        links = soup.find_all('a')

        for link in links:
            link = link.contents[0]
            #check file ending
            extensionLoc = link.find(".txt")
            if extensionLoc >= 0:
                #check for good filename (not a readme or somesuch)
                if re.search('[A-Za-z]', link[:extensionLoc]) is None:
                    return requests.get(BASE_URL + str(bookNum) + "/" + link).text
        maxAttempts -= 1
    return "No retrievable text found"

def parseBookDetails(core):
    detailsLoc = [core.find("Title: "), core.find("Author: "), core.find("Language: ")]
    dOffset = [len("Title: "), len("Author: "), len("Language: ")]
    details = []
    for loc, i in enumerate(detailsLoc):
        if i != -1:
            i += dOffset[loc]
            details.append(core[i:core[i:].find('\r\n')+i])
        else:
            details.append(None)
    return details

def makeTag(details):
    tag = "\n ~"
    if(details[0] != None):
        tag += details[0]
        if(details[1] != None):
            tag += ", "
    if(details[1] != None):
        return tag + details[1]
    return tag + "Unknown"

def parseBook(core, tag):
    bodyTag = "PROJECT GUTENBERG EBOOK"
    start = core.find(bodyTag)
    end = core.rfind(bodyTag)
    #very rare for this if to fail, but Project Gutenberg is only 99% consistent in its formatting...
    #we're in god's hands now
    if start != -1 and end != -1:
        core = core[start:end]
    core = core.replace('\r\n', ' ')
    sents = nltk.sent_tokenize(core)
    #remove all uppercase chapter headings
    for loc, sent in enumerate(sents):
        if re.search(r'[a-z]', sent) == None:
            sents.pop(loc)
    return [sents[q] for q in range(len(sents)) if len(sents[q]) < 140-len(tag) and len(sents[q]) > 40]

#############################################################################
#       Third section- gather probabilities on quotes and select one.       #
#############################################################################

def quoteProb(quote, freqs):
    #space period for sentence parsing
    if quote[len(quote)-1] == '.':
        quote = quote[:len(quote)-1] + " ."
    qWords = nltk.word_tokenize("} { " + quote[:len(quote)-1].lower() + " . } {")
    
    stemmer = nltk.stem.snowball.SnowballStemmer("english")
    for loc,word in enumerate(qWords):
        qWords[loc] = stemmer.stem(word)
        
    groups = [qWords[j:j+3] for j in range(len(qWords)-2)]
    desiredNovelty = 1 #amount of unpenalized unseen bigrams
    sentenceProb = 0
    for i in range(len(groups)):
        try:
            sentenceProb += math.log(freqs.prob(groups[i]))
        except ValueError:
            desiredNovelty -= 1
    return sentenceProb/len(qWords) - freqs.prob(freqs.max())*math.fabs(desiredNovelty)

def getQuote(core, lang, KN):
    #ugly clean-up from sentence parsing
    def polish(finalQuote):
        if finalQuote.count("\"") % 2 != 0:
            finalQuote = finalQuote.replace("\"", "", 1)
        if finalQuote[0].islower():
            finalQuote = finalQuote.capitalize()
        return re.sub(r' +', ' ', finalQuote.replace("\"", "\'"))
    
    if(lang != "English"):
        return polish(core[random.randint(0, len(core)-1)])
    quoteProbs = []
    print len(core)
    for i in range(len(core)):
        quoteProbs.append(quoteProb(core[i], KN))
        if i % 250 == 0:
            print i
    DEVIATION_FROM_BEST = .5
    core = zip(core, quoteProbs)
    core = sorted(core, key = lambda core:core[1], reverse=True)
    bestQuotes = []
    for i in core:
        if i[1] > core[0][1] - DEVIATION_FROM_BEST:
            #check against weird quotes
            #(no non-alphanumerics, has lower case letters, len > 4)
            if re.search('[^\d\s\w\!.\?\(\)]', i[0]) is None \
              and re.search('[a-z]', i[0]) is not None \
              and len(i[0]) > 4:
                bestQuotes.append(i)
    print bestQuotes
    return polish(bestQuotes[random.randint(0, len(bestQuotes)-1)][0])

def tweet(quote):
    auth = tweepy.OAuthHandler(secrets.CONSUMER_KEY, secrets.CONSUMER_SECRET)
    auth.set_access_token(secrets.ACCESS_TOKEN, secrets.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    api.update_status(status=quote)

def main():
    quoteObj = json.load(open("authorQuotes.json", 'rb'))
    KN = buildQuoteFreq(quoteObj)
    core = getBook()
    details = parseBookDetails(core)
    tag = makeTag(details)
    core = parseBook(core, tag)
    if core == []:
        quote = "A facility for quotation covers the absence of original thought. \n~ Dorothy L. Sayers, Gaudy Night"
    else:
        quote = getQuote(core, details[2], KN)+tag
    tweet(quote)
main()
