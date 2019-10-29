const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({headless: true, devtools: false});
    // const browser = await puppeteer.launch({headless: false, devtools: true});
    const page = await browser.newPage();
    await page.goto('https://www.baidu.com/');

    await page.click('#kw');
    page.keyboard.type('时间');
    await page.click("#su");
    // await page.waitForNavigation({ waitUntil: 'networkidle2' });
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



