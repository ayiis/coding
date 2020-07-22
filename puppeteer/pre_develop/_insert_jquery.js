const fse = require('fs-extra'); // v 5.0.0

async function insert_jquery_0(page) {
    const rand_str = `/${Math.random().toString(36)}`;  // 插入jQuery
    page.on('request', async(interceptedRequest) => {
        const url = new URL(interceptedRequest.url());
        if (url.pathname && url.pathname[0] == "/") {
            ;
        }
        if (url.pathname === rand_str) {
            console.log("Insert jQuery...");
            const buffer= await fse.readFile("/mine/github/coding/puppeteer/stage_script/_data_/jquery.min.js");
            interceptedRequest.respond({
                status: 200,
                body: buffer,
            });
            return;
        } else {
            return interceptedRequest.continue();
        }
    });

    return rand_str;
}

async function insert_jquery_1(page, rand_str) {

    // 动态插入 jquery
    await page.evaluate(rand_str => {
        document.body.appendChild(document.createElement("script")).setAttribute("src", rand_str);
    }, rand_str);

    await page.waitForResponse(response => {
        // 等到 jquery 加载完毕返回 true 时，方法执行完毕
        return response.request().url().endsWith(rand_str);
    });
    console.log("jQuery inserted ok!");

    // 检查 jquery 是否已经生效
    await page.waitForFunction("!!window.jQuery");
    console.log("jQuery works good!");
}

module.exports.insert_jquery_0 = insert_jquery_0;
module.exports.insert_jquery_1 = insert_jquery_1;
