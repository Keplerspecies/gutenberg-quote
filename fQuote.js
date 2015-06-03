	var SENTENCE_SPLIT_TOKEN 	= ". ",
	TEXT_OFFSET_PERCENT 	= .1,
	TWITTER_CHAR_LIMIT		= 140;

module.exports = {

	//Gutenberg books have semi-standardized legal precludes.
	//Handle this the best you can, there may be an occasional wrong quote
	splitBook: function (book){

		/* Shave off the top and bottom of the document. Hopefully
		** enough to remove pre- and post-scripts. It's in God's hands... 
		** If repeatedly failing, raise TEXT_OFFSET PERCENT*/
		book = book.substring(book.length*TEXT_OFFSET_PERCENT, book.length*(1-TEXT_OFFSET_PERCENT));

		console.log(book.indexOf(""));
		book = book.replace("\r\n", "");
		book = book.split(SENTENCE_SPLIT_TOKEN);
		return book;
	},

	findQuote: function (book, author, title){
		/*This will be in a function when I have an internet connection, and be called by
		quoteBot.js. Remember to change to variable that is TWITTER_CHAR_LIMIT - author, title */
		var sig =  "\r\n\t ~" + author + ", " + title;
		var quoteLimit = TWITTER_CHAR_LIMIT -sig.length;
		var quote = "";

		do{
			var
			quote = book[Math.floor(Math.random()*book.length)].replace("\r\n", " ");
			//quote = quote.replace("\r\n", "");
		}while(quote.length > quoteLimit);
		return quote+sig;
	}
};