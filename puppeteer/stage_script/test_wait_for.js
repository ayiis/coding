const puppeteer = require('puppeteer');
const fse = require('fs-extra'); // v 5.0.0
const _ = `
    1. wait for network done 
    1. body load
    1. load another page
    2. wait for element appeared
    3. wait for button clicked
    4. wait for js execute
    5. wait for a reuqest
    6. wait for anything(with a function)
    7. wait for ajax 
        request.resourceType() === 'xhr'
`;

const target_page = 'https://fanyi.baidu.com';

async function human_type(page, sentence) {
    // delay 15~45ms for each press
    for(var i = 0 ; i < sentence.length ; i++ ) {
        if(/^[a-zA-Z]$/.test(sentence[i])) {
            await page.keyboard.type(
                sentence[i], 
                {delay: parseInt(Math.random() * 10000 % 30 + 15)}
            );
        } else {
            await page.keyboard.type(
                sentence[i], 
                {delay: parseInt(Math.random() * 10000 % 60 + 55)}
            );
        }
    }
}

// wait until all request is done for at least `timeout` ms.
// from https://github.com/jtassin/pending-xhr-puppeteer/blob/master/src/index.ts
async function networkidle_timeout(page, timeout=500, max_timeout=30000) {
    let padding_request_set = new Set([]);
    const callback_request = function(request) {
        // Some types of request that worth waiting for
        if (['xhr', 'script', 'document', 'text/html', 'text/plain'].indexOf(request.resourceType()) !== -1) {
            padding_request_set.add(request);
        }
    }
    const callback_requestfailed = function (request) {
        padding_request_set.has(request) && padding_request_set.delete(request);
    }
    const callback_requestfinished = function (request) {
        padding_request_set.has(request) && padding_request_set.delete(request);
    }
    page.on('request', callback_request);
    page.on('requestfailed', callback_requestfailed);
    page.on('requestfinished', callback_requestfinished);

    let total_time = 0;
    let count_timeout = 0;
    let split_timeout = timeout / 5;
    while(count_timeout < timeout) {
        if (padding_request_set.size > 0) {
            count_timeout = 0 ;
        } else {
            count_timeout += split_timeout;
        }
        total_time += split_timeout;
        if (max_timeout < total_time) {
            break;
        }
        await page.waitFor(split_timeout);
    }

    // clear all listener
    page.removeListener("request", callback_request);
    page.removeListener("requestfailed", callback_requestfailed);
    page.removeListener("requestfinished", callback_requestfinished);
}

(async () => {

    const browser = await puppeteer.launch({headless: true, devtools: false});
    // const browser = await puppeteer.launch({headless: false, devtools: true});

    const context = browser.defaultBrowserContext();
    context.clearPermissionOverrides();
    await context.overridePermissions(target_page, ['clipboard-read', 'clipboard-write']);

    const page = await browser.newPage();
    const rand_str = `/${Math.random().toString(36)}`;
    const url = 'https://fanyi.baidu.com/';

    const 
        WF_NEWWORK_DONE = true,
        WF_BODY_LOAD = true,
        WF_ELEMENT_APPEARED = true,
        WF_BUTTON_CLICKED = true,
        WF_JS_EXECUTE = true,
        WF_REUQEST = true,
        WF_AJAX = true,
        WF_FUNCTION = true;

    if(WF_REUQEST === true) {
        await page.setRequestInterception(true);
        page.on('request', async(interceptedRequest) => {
            const url = new URL(interceptedRequest.url());
            if (url.pathname !== rand_str) {
                return interceptedRequest.continue();
            }
            const buffer= await fse.readFile('_data_/nothing.js');
            interceptedRequest.respond({
                status: 200,
                body: buffer,
            });
        });
    }

    if(WF_NEWWORK_DONE === true) {
        await page.goto(url, {waitUntil: 'networkidle2'});
    }

    if(WF_BODY_LOAD === true) {
        await page.reload({waitUntil: 'networkidle2'});
    }

    if(WF_ELEMENT_APPEARED === true) {
        await page.mainFrame().waitForSelector('.select-to-language>.select-inner>.language-selected');
    }

    if(WF_REUQEST === true) {
        const add_script = await page.evaluate(rand_str => {
            document.body.appendChild(document.createElement('script')).setAttribute('src', rand_str);
            return true;
        }, rand_str);

        if (add_script) {
            await page.waitForResponse(response => {
                // callback indefinite times until return `true`
                return response.request().url().endsWith(rand_str);
            });
        }

        if (WF_FUNCTION === true) {
            await page.waitForFunction('window.status === "nothing"');
        }
    }

    if(WF_BUTTON_CLICKED === true) {
        const button_select_fl = '.select-from-language';
        await page.mainFrame().waitForSelector(button_select_fl, {visible: true});
        await page.click(button_select_fl);
    }

    if(WF_BUTTON_CLICKED === true) {
        const button_swe = '.from-language-list .language-list .data-lang[value=swe]';
        await page.mainFrame().waitForSelector(button_swe, {visible: true});
        await page.click(button_swe, {delay: 20});
    }

    if (WF_JS_EXECUTE === true) {
        await page.waitForFunction('$(".select-from-language .language-selected").text().trim() === "瑞典语"');
    }

    await page.click('#baidu_translate_input', {delay: 20});

    await human_type(page, "Allt Jag Vill Ha");   // 我想要的一切

    if(WF_AJAX === true) {
        // wait for translation
        await networkidle_timeout(page, 500);
    }

    const content = await page.evaluate(() => {
        return $('.target-output').text().trim();
    });

    console.log(content);

    await browser.close();

})();
