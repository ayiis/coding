const puppeteer = require('puppeteer');
const fse = require('fs-extra'); // v 5.0.0

(async () => {
    const browser = await puppeteer.launch({headless: true, devtools: false});
    // const browser = await puppeteer.launch({headless: false, devtools: true});
    const page = await browser.newPage();
    const rand_str = `/${Math.random().toString(36)}`;
    const url_list = [
        'https://www.amobbs.com/thread-5682512-1-1.html',
        'https://www.amobbs.com/thread-5667632-1-1.html',
    ];

    await page.setRequestInterception(true);
    page.on('request', async(interceptedRequest) => {
        const url = new URL(interceptedRequest.url());
        if (url.pathname !== rand_str) {
            return interceptedRequest.continue();
        }
        const buffer= await fse.readFile('_data_/jquery.min.js');
        interceptedRequest.respond({
            status: 200,
            body: buffer,
        });
    });

    for(var i = 0 ; i < url_list.length ; i++) {
        const url = url_list[i];
        await page.goto(url);
        await page.mainFrame().waitForSelector('#postlist');

        const add_jquery = await page.evaluate(rand_str => {
            if(!window.jQuery) {
                document.body.appendChild(document.createElement('script')).setAttribute('src', rand_str);
                return true;
            }
            return false;
        }, rand_str);

        if (add_jquery) {
            await page.waitForResponse(response => {
                // callback indefinite times until return `true`
                return response.request().url().endsWith(rand_str);
            });
        }

        await page.waitForFunction('!!window.jQuery');
        // page.waitForFunction('window.status === "ready"');

        const content = await page.evaluate(() => {
            return $('#postlist>div:first .t_f').text();
        });

        console.log(content);

        console.log("=-=-=-=-=-=-=-=-=-=-= =-=-=-=-=-=-=-=-=-=-= =-=-=-=-=-=-=-=-=-=-= =-=-=-=-=-=-=-=-=-=-= =-=-=-=-=-=-=-=-=-=-= =-=-=-=-=-=-=-=-=-=-= =-=-=-=-=-=-=-=-=-=-= =-=-=-=-=-=-=-=-=-=-=");

    }

    await browser.close();
})();


// const output_dir = './amobbs';
// start('https://www.amobbs.com/thread-5667632-1-1.html');
