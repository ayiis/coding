// * Response interception https://github.com/GoogleChrome/puppeteer/issues/1191

const puppeteer = require('puppeteer')


const domains_in_blacklist = [
    "www.baidu.com",
    "ss1.bdstatic.com",
    "hm.baidu.com",
    "pcw-api.iqiyi.com",
    "www.iqiyi.com",    // block main site
]

const requests_blocked = []

// puppeteer.launch({headless: false, devtools: true}).then(async browser => {
puppeteer.launch({ headless: true, devtools: false }).then(async browser => {
    const page = await browser.newPage()

    await page.setRequestInterception(true)
    page.on('request', interceptedRequest => {
        const url = new URL(interceptedRequest.url())
        if (domains_in_blacklist.includes(url.host) || /(image|stylesheet)$/.test(interceptedRequest.resourceType())) {
            requests_blocked.push(interceptedRequest.url())
            interceptedRequest.abort()
        } else {
            console.log(`[${interceptedRequest.resourceType()}] - ${interceptedRequest.url()}`)
            interceptedRequest.continue()
        }
    });
    page.on('response', response => {
        console.log(`[${response.status()}] - ${response.remoteAddress().ip}:${response.remoteAddress().port} - ${response.url()}`);
    });

    try {
        await page.goto('https://www.iqiyi.com/')
    } catch (err) {
        console.log(err.message)    // 'net::ERR_FAILED at https://www.baidu.com'
    }

    await browser.close()
});
