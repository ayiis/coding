// A BUG of chromium
// https://github.com/GoogleChrome/puppeteer/issues/795
// https://bugs.chromium.org/p/chromium/issues/detail?id=771825
const http = require('http');
const puppeteer = require('puppeteer');
const iconv = require('iconv-lite');

const ORIGINAL_DATA = Buffer.from(JSON.stringify({'msg': '测试'}));


function serve() {
    http.createServer(function (req, res) {
        // The correct header should be 'application/json; charset=utf-8'
        // but I change it to 'text/plain' to  REPRODUCE THE BUG
        res.setHeader('Content-Type', 'text/plain');
        res.writeHead(200);
        res.end(ORIGINAL_DATA);
    }).listen(8001);

}

async function responseSuccess(res) {
    let dataReceived = await res.buffer();
    console.log('Received:\n', dataReceived);
    console.log('Original:\n', ORIGINAL_DATA);
    console.log('\n');
    debugger;
    iconv.decode(dataReceived, 'utf8');
}

async function doRequest() {
    const browser = await puppeteer.launch({headless: true});
    const page = await browser.newPage();
    page.on('response', responseSuccess);
    let res = await page.goto('http://localhost:8001');
    await browser.close();
}


serve();
doRequest();
