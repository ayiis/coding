const fse = require("fs-extra");
const local_path = "/mine/github/coding/puppeteer/common";

async function insert_local_js_file(page, file_path) {
    /*
        1. 拦截请求，指定某一个特定的请求为 file_path
        2. 在页面html里，动态插入 file_path 请求
    */
    const rand_str = `/${Math.random().toString(36)}`;
    await page.setRequestInterception(true);
    async function request_intercept(interceptedRequest) {
        const url = new URL(interceptedRequest.url());
        if (url.pathname === rand_str) {
            console.log("Catch the js file reuqest:", rand_str);
            const buffer= await fse.readFile(file_path);
            interceptedRequest.respond({
                status: 200,
                body: buffer,
            });
            return;
        } else {
            return interceptedRequest.continue();
        }
    }
    page.on("request", request_intercept);

    // 动态插入 js 文件
    await page.evaluate(rand_str => {
        document.body.appendChild(document.createElement("script")).setAttribute("src", rand_str);
    }, rand_str);

    await page.waitForResponse(response => {
        // 等到 js 文件 加载完毕时，返回 true，方法执行完毕
        return response.request().url().endsWith(rand_str);
    });
    console.log("Js file insert ok:", file_path);

    page.off("request", request_intercept);
    await page.setRequestInterception(false);
}

async function insert_jquery(page) {
    /*
        1. 插入 jQuery.js 文件
        2. 检查 jQuery 是否已经生效
    */
    const jquery_path = `${local_path}/_js_files_/jquery.min.js`;
    await insert_local_js_file(page, jquery_path);

    // 检查 jquery 是否已经生效
    await page.waitForFunction("!!window.jQuery");
    console.log("jQuery works good!");

    /*
        1. 插入 scrollTo.js 文件
        2. 检查 scrollTo 是否已经生效
    *//*

    const jquery_scrollto_path = `${local_path}/_js_files_/jquery.scrollTo.min.js`;
    await insert_local_js_file(page, jquery_scrollto_path);

    // 检查 scrollTo 是否已经生效
    await page.waitForFunction("!!$.scrollTo");
    console.log("scrollTo works good!");
    */
}

module.exports = {
    "insert_local_js_file": insert_local_js_file,
    "insert_jquery": insert_jquery,
};
