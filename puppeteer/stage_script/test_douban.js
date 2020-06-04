const puppeteer = require('puppeteer');

(async () => {

    const browser = await puppeteer.launch({
        executablePath: '/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome',
        userDataDir: '/tmp/tmp',
        // headless: true,
        devtools: false,
        headless: false,
        // devtools: true,
        slowMo: 10,
        defaultViewport: null
    });
    const page = await browser.newPage();
    await page.goto('https://www.douban.com/group/?start=0', { waitUntil: 'networkidle2' });

    $('#content').find("table>tbody>tr");

    for(var i = 0; i < 3; i++) {
        await page.click('#content .next');
        await page.waitForNavigation({ waitUntil: 'networkidle2' });
    }

    // https://www.douban.com/group/?start=50
    // await browser.disconnect();

    return;

    debugger;

    $('#content .next')

    await page.click('#content .next');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });

    await page.mainFrame().waitForSelector('.op-beijingtime-time');

    const href_list = await page.evaluate(() => {
        return $('#content_left>div').map(function(){ return $(this).find('.t:eq(0)>a').attr('href'); }).toArray();
    });
    var good_count = 0;
    var match_start = "http://www.baidu.com/link?url=";
    for(var i = 0; i < href_list.length; i++) {
        var href = href_list[i];
        if(href.substr(0, match_start.length) == match_start){
            good_count = good_count + 1;
        }
    }
    console.log(good_count);
    await browser.close();
})();



