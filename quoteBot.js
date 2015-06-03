var request = 	require('request'),
    cheerio = 	require('cheerio'),
    async 	= 	require('async'),
    fQuote	=	require('./fQuote.js');

var baseURL 	= 'http://www.gutenberg.org/',
	listingURL	= "dirs/GUTINDEX.ALL",
	bNumURL		= "",
	txtName		= "";

/* All the following constants are determined by the (rather inconsistent) 
** specifications at the main Gutenberg book listing, 
** http://www.gutenberg.org/dirs/GUTINDEX.ALL */
var AUTHOR_SPLIT_TOKEN = ", by ",
	PREFIX_SPLIT_TOKEN = "ETEXT NO.\r\n\r\n",
	POSTFIX_SPLIT_TOKEN = "<==End of GUTINDEX.ALL==>",
	BOOK_ENTRY_SPLIT_TOKEN = "\r\n\r\n",
	BOOK_DETAIL_SPLIT_TOKEN = "\r\n";


var bNum, bTitle, bAuthor;//b for book!

var causeLoop = false;

//HOW QUOTEBOT WORKS
/* Quotebot could work by random selecting from a giant preordained list of quotes. That isn't really
** much fun. Rather, quotebot looks through the Project Gutenberg online archives, randomly selects a
** book of all currently available books, and then selects a quote from that. */

//HOW GUTENBERG ORDERING WORKS
/* Project Gutenberg orders files by under each folder for each digit.
** For example, file 1234 will be held at baseURL/1/2/3/4.
** So, the first method in the async series parses the main listing to find how many bs there 
** currently are, and randomly selects one from that */

async.series([
	//request call to general directory
	function(callback){
		request(baseURL + listingURL, function (error, response, body) {
		    if(!error && response.statusCode == 200) {
		    	do {
			    	/* There is no single listing format in the Gutenberg ASCII file.
			    	** I have elected to go with the most prominent one, however
			    	** This reduces the number of usable books by about 10,000 */
			      	body = body.substring(body.indexOf(PREFIX_SPLIT_TOKEN) + PREFIX_SPLIT_TOKEN.length,
			    						body.lastIndexOf(POSTFIX_SPLIT_TOKEN)); //crop the gibberish
			      	bListing = body.split(BOOK_ENTRY_SPLIT_TOKEN);
			      	var bIndex = Math.floor(Math.random() * bListing.length);
			      	var bDetails = bListing[bIndex].split(BOOK_DETAIL_SPLIT_TOKEN);
			      	/* REMOVE POTENTIAL LETTERS */
			      	bNum = bDetails[0].substring(bDetails[0].lastIndexOf(' ')+1);
			      	bDetails[0] = bDetails[0].substring(0, bDetails[0].lastIndexOf(' ')).trim();
			      	bTitle = bDetails[0].split(AUTHOR_SPLIT_TOKEN)[0];
			      	bAuthor = bDetails[0].split(AUTHOR_SPLIT_TOKEN)[1];
			      	/* AUTHOR COULD BE ON SEPERATE LINE */
			      	/* AUTHOR COULD HAVE [] */

			      	//repeat if 
			      	  //any value is null
			      	if((!bNum || !bTitle || !bAuthor) ||
			      	  //is not a book
			      	  (bTitle.indexOf("Audio") != -1) ||
			      	  //is one of the few unused unfilled indices
			      	  (bTitle.toLowerCase().indexOf("not used") != -1))
			      		causeLoop = true;
			      	else
			      		causeLoop = false;

			      	//clean-up potential extra gibberish
			      	//e.g. bAuthor= Henri Bergson   [laemcxxx.xxx]
			      	if(bAuthor && bAuthor.indexOf("[") !== -1)
			      		bAuthor = bAuthor.substring(0, bAuthor.indexOf("[")).trim();

			      }while(causeLoop === true);
			callback(null, 'one');
		    }
		});
	},
	//request call to random given subdirectory
	function(callback){
		request(baseURL + "files/" + bNum, function (error, response, body){
			//console.log(body);
			if(!error && response.statusCode == 200){
		        var $ = cheerio.load(body);
		        $('td:nth-child(2)').each(function () {
		            if($(this).text().indexOf(".txt") !== -1){
		            	txtName = $(this).text();
		            	return false;
		            }		
		        });
		    }
		    console.log(txtName);
		    callback(null, 'two');
		});
	},
	//request .txt file
	function(callback){
		request(baseURL + "files/" + bNum + "/" + txtName, function (error, response, body){
			//console.log(body);
			book = fQuote.splitBook(body);
			quote = fQuote.findQuote(book, bAuthor, bTitle);
			console.log(baseURL + "files/" + bNum + "/" + txtName);
			console.log(bNum);
			console.log(bTitle);
			console.log(bAuthor);
			console.log(quote);
			callback(null, 'three');
		});
	}
]);