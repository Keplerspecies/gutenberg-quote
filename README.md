# Gutenberg Quote
A twitter bot for posting quotes from Project Gutenberg texts.

View at https://twitter.com/gutenbergquote

Gutenberg Quote is a twitter bot designed to parse a random [Project Gutenberg](http://www.gutenberg.org/) 
book and pick an 'optimal' quote from it. It does this by using a corpus based on a [Wikiquotes 06/02/15 Database Dump](https://dumps.wikimedia.org/enwikiquote/20150602/).
The makeshift XML parser to convert this dump to JSON is included here. The function reduceJSON is included at the bottom of this,
and can be called using a CSV list of names (like, as I did, a webscrape of [a list of authors](https://en.wikiquote.org/wiki/Category:Authors))
to further filter the data.

To use (assuming you have a corpus), fill secrets.py with the necessary OAuth tokens, and run the quoteBot script. 
It is also recommended that variable MAX_BOOKS (found in getBook()) be updated to the 
[current amount of Gutenberg texts](http://www.gutenberg.org/dirs/GUTINDEX.ALL.iso-8859-1.txt).

Uses [nltk](https://github.com/nltk/nltk/), [tweepy](http://tweepy.readthedocs.org/en/v3.2.0/), and 
[beautiful soup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/).
