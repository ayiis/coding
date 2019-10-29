var dateFormat = require('dateformat');
var now = new Date().getTime();

// Basic usage
// a = dateFormat(now, "dddd, mmmm dS, yyyy, h:MM:ss TT");
// Saturday, June 9th, 2007, 5:46:21 PM

console.log(now - 1000*60*60*4);

now = new Date(now - 1000*60*60*8).getTime();


a = dateFormat(now, "yyyymmddHHMMss");

console.log(a);


new Date(new Date().getTime() - 1000*60*60).toISOString()
