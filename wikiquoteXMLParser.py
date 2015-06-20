
# coding: utf-8

# In[2]:

import xml.etree.ElementTree as ET, re, json, sys, csv
from nltk.corpus import stopwords

i = 0
TWIT_LOWER_LIM = 20
TWIT_UPPER_LIM = 140
CUTOFF_WORDS = ["See also=", "See also ", "External links", "Cast =", "Cast="]
SKIP_TITLE = ["Wikiquote", "Talk", "User", "List"]
FILE_NAME = "enwikiquote-20150602-pages-meta-current.xml"

def isEnglish(text):
    #include numbers
    text = text.split(" ")
    STOPWORDS = set(stopwords.words('english'))
    #check if in english... if not, translation SHOULD be right below
    if len(STOPWORDS.intersection(text)) / float(len(text)) < .175:
        #print len(STOPWORDS.intersection(text)) / float(len(text))
        return False
    return True

#remove some of the (very basic) text/HTML markup in wiki that may obscure quote text. 
#Simple enough not to need parser, I hope
def dewiki(text):
    def linkReplace(link):
        link = link.group()
        newLink = link[len('[['):(len(link)-len(']]'))]
        barLoc = newLink.find('|')
        if(barLoc == -1):
            return newLink
        return newLink[barLoc+1:]
    #remove comments
    text = re.sub('\[\[.*?\]\]', linkReplace, text)
    #remove empty html tags(how did that get in there?)
    text = re.sub('<.*?>', ' ', text)
    #remove italics, bold
    text = re.sub('\'{2,}|\*{2}|\[\]', '', text)
    #remove potential extra spaces
    text = re.sub(' +', ' ', text)
    if "English equivalent:" in text:
        text = text[len("English equivalent:"):]
    if "English:" in text:
        text = text[len("English:"):]
    elif "Translation:" in text:
        text = text[len("Translation:"):]
    return text.strip()

def grabQuote(text):
    text = text.split('\n')
    if(isEnglish(text[0])):
        return dewiki(text[0])
    #print "TEXT" + text[0]
    try:
        return dewiki(text[1])
    #No translation available? Assume it's underneath anyway
    except IndexError:
        #print "HORRIBLE ERROR!"
        return dewiki(text[0])

def grabQuotes(text):
    #improve this regex
    text = text.split("\n* ")
    #don't care about opening lines, just looking for quotes
    text.pop(0)
    quoteListing = []
    for textSplit in text:
        quote = grabQuote(textSplit)
        #check for word limit, punctuation and gibberish (really only care about ascii here...)
        if (len(quote) < TWIT_UPPER_LIM and len(quote) > TWIT_LOWER_LIM 
          and re.search('[^A-Za-z ;\'\,\"\.\!\?]', quote) is None
          and re.search('[.\!\?]', quote) is not None):
            quoteListing.append(quote)
    return quoteListing
        

iter = ET.iterparse(FILE_NAME)
#root = tree.getroot()


# In[3]:


contTag = False
quoteObj = {}
Author = ""
for event, elem in iter:
    #print elem.tag, elem.attrib
    i+=1
    if(i%100000 == 0):
        print i
    #if(i==100):
    #    break
    #print i
    if "page" in elem.tag:
        for page in elem:
            #avoid administrative pages
            if 'title' in page.tag:
                for skipTitle in SKIP_TITLE:
                    if skipTitle in page.text:
                        contTag = True
                        break
                author = page.text
            if "revision" in page.tag:
                if contTag:
                    contTag = False
                    continue
                for rev in page:
                    if "text" in rev.tag:
                        text = rev.text
                        if text is None:
                            continue
                        cutoff = sys.maxsize
                        for cutoff_word in CUTOFF_WORDS:
                            temp = text.find(cutoff_word)
                            if temp != -1:
                                cutoff = min(cutoff, temp)
                            text = text[:cutoff]
                        text = grabQuotes(text)
                        if bool(text):
                            quoteObj[author] = text
if bool(quoteObj):
    with open("quotes.json", 'ab') as out:
        json.dump({"Authors": quoteObj}, out, sort_keys=True, indent=4, separators=(',', ':'))
                            


# In[34]:

#can be called on output file give a CSV file of names to reduce dataset
def reduceJSON(jsonName, csvName, outName)
    quoteObj = json.load(open("quotes.json", 'rb'))
    authors = {}
    #print quoteObj["Authors"].keys()
    with open("wikiauthors.csv", 'rb') as authList:
        authListReader = csv.reader(authList)
        authListReader.next()
        for author in authListReader:
            if author[0].decode('utf') in quoteObj["Authors"].keys():
                for x in quoteObj["Authors"][author[0].decode('utf')]:
                    i+=1
                authors[author[0]] = quoteObj["Authors"][author[0].decode('utf')]

    with open("authorQuotes.json", 'wb') as out:
        json.dump({"Authors" : authors}, out, sort_keys=True, indent=4, separators=(',', ':'))

