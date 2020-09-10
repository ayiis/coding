const puppeteer = require('puppeteer');
const fse = require('fs-extra'); // v 5.0.0
const { URL } = require('url');
const path = require('path');
const mongo = require('mongodb');
const https = require('https');
const fs = require('fs');
const ppt_insert_jquery = require('./_insert_jquery.js');
/*

✅ 0. 打开起始页面
    https://time.geekbang.org/column/article/14252

        ✅ 获取专栏名称
        - 获取专栏下的所有课程

⚠️ 1. 遍历目录，取得课程列表，不断下拉，直到（移动鼠标，滑动） [暂时不需要]
    接口：https://time.geekbang.org/serv/v1/column/articles
    返回：RESPONSE["data"]["page"]["more"] == false

✅ 2. 打开文章页面

✅ 3. 点击沉浸模式
    $('.P00Ux77Z_0').click();
    或者：
    $("#wechat-share").prev().prev().click();

⚠️ 4. 处理评论，如果需要评论，不断下拉，直到（移动鼠标，滑动）
    接口：https://time.geekbang.org/serv/v1/comments
    返回：RESPONSE["data"]["page"]["more"] == false

    - 如果不需要评论，直接删除

5. 计算并补充 height

6. 保存为pdf

    张磊.深入剖析Kubernetes/14252.开篇词 | 打通“容器技术”的任督二脉.pdf

*/
const settings = {
    // "start_page": "https://time.geekbang.org/column/article/4906",
    "start_page": "https://time.geekbang.org/column/article/14252",
    // "start_page": "https://readhub.cn/topics",

    "page_base": "https://time.geekbang.org/column/article/",

    "elem.1.专栏标题标签": "._3sZn_BpW_0",

    // 点击沉浸模式 获得更简洁的页面布局
    "elem.1.沉浸模式": ".P00Ux77Z_0",
    "elem.2.沉浸模式": "#wechat-share",
}

// 目标资源的请求地址 - 专栏文章列表接口
const target_url_article_list = {
    "hostname": "time.geekbang.org",
    "pathname": "/serv/v1/column/articles",
}
// 目标资源的请求地址 - 专栏章节列表接口
const target_url_chapter_list = {
    "hostname": "time.geekbang.org",
    "pathname": "/serv/v1/chapters",
}

async function sleep(sec) {
    return new Promise(resolve => setTimeout(resolve, 1000*sec));
}

async function fse_create_file(file_name) {
    return new Promise(resolve => fse.ensureFile(file_name, resolve));
}

async function scroll_to_bottom(page, max_try) {

    max_try = max_try || 9;
    let stop_mark = 3;
    let prev_height = 0;

    // 下拉，直到所有评论都刷出来，或者达到9次
    for(let i = 0; i < max_try; i ++) {

        // await page.keyboard.down('Control');
        // await page.keyboard.press('KeyF');
        // await page.keyboard.up('Control');

        await page.evaluate(() => {
            var max_height = Math.max.apply(this, $(".simplebar-content").map(function(){ return $(this).height()}));
            $("#app").find(">div:first").height(max_height);

            $("html, body").animate({ scrollTop: max_height - 600 }, 500);
            setTimeout(function() {
                $("html, body").animate({ scrollTop: max_height + 600 }, 500);
            }, 1000);
        });

        break;

        await sleep(4);

        let now_height = await page.evaluate(() => {
            return $(document).height();
        });
        console.log("Now height:", now_height);

        if (prev_height == now_height) {
            stop_mark -= 1;
            if (stop_mark <= 0) {
                console.log("Seems reach the bottom:", now_height);
                break;
            }
        } else {
            stop_mark = 3;  // 重置标记值
            prev_height = now_height;
        }
    }
}

async function valid_deepin_exists(page) {

    let deepin_exists = await page.evaluate(elem_name => {
        return $(elem_name).length == 1;
    }, settings["elem.1.沉浸模式"]);

    if(deepin_exists) {
        await page.evaluate(elem_name => {
            $(elem_name).click();
        }, settings["elem.1.沉浸模式"]);
    } else {
        console.log("[Warning]: Check fail: 沉浸模式 not exists!");
        await page.evaluate(elem_name => {
            $(elem_name).prev().prev().click();
        }, settings["elem.2.沉浸模式"]);
    }

    return true;
}

;(async () => {

    // 配置 puppeteer 使用固定的 Chrome，预先输入登录信息
    const browser = await puppeteer.launch({
        executablePath: "/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome",
        userDataDir: "/tmp/tmp",
        // userDataDir: "/tmp/tmp2",
        headless: true,
        devtools: false,
        // headless: false,
        // devtools: true,
        slowMo: 20,
        defaultViewport: null,
        args: [
            "--window-size=1920,1080",
        ],
    });

    const context = browser.defaultBrowserContext();
    await context.clearPermissionOverrides();

    // 0. 打开起始页面
    const page = await browser.newPage();
    await page.setUserAgent("user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36");
    await page.setRequestInterception(true);

    // 文章列表保存到此变量
    let article_list = [];
    let article_list_ok = false;
    let chapter_map = {};

    // 监听文章列表接口
    page.on("response", async (response) => {
        const url = new URL(response.url());
        if (response.status() !== 200){
            return;
        }
        // 章节信息 - 接口解析
        if (
            url.hostname == target_url_chapter_list["hostname"] 
            && url.pathname == target_url_chapter_list["pathname"]
        ) {
            let chapter_list_content = await response.buffer();
            chapter_list_content = chapter_list_content.toString("utf8");
            console.log("Got target_url_chapter_list data:", chapter_list_content.length);
            chapter_list_content = JSON.parse(chapter_list_content);
            chapter_list_content["data"].forEach(function(item) {
                chapter_map[item.id] = item.title;
            });
        }
        // 文章列表信息 - 接口解析
        else if (
            url.hostname == target_url_article_list["hostname"] 
            && url.pathname == target_url_article_list["pathname"]
        ) {
            let article_list_content = await response.buffer();
            article_list_content = article_list_content.toString("utf8");
            console.log("Got target_url_article_list data:", article_list_content.length);
            article_list_content = JSON.parse(article_list_content);
            for(let i = 0; i < 9 ; i++ ) {
                article_list_content["data"]["list"].forEach(function(item) {
                    article_list.push({
                        "id": item.id,
                        "author_name": item.author_name,
                        "chapter_id": item.chapter_id,
                        "article_title": item.article_title,
                    });
                });

                if(article_list_content["data"]["page"]["more"] == false) {
                    console.log("reach api end!");
                    break;
                } else {
                    // TODO ⚠️ 1
                    break;
                }
            }
            article_list_ok = true;
        }
    });

    const rand_str = await ppt_insert_jquery.insert_jquery_0(page);
    await page.goto(settings["start_page"], {waitUntil: "networkidle0"});
    await ppt_insert_jquery.insert_jquery_1(page, rand_str);

    await page.screenshot({path: "base_page.0.png", fullPage: true, format: "A4"});

    // 额外等待6秒
    await sleep(6);
    await page.screenshot({path: "base_page.1.png", fullPage: true, format: "A4"});

    // 点击沉浸模式
    await valid_deepin_exists(page);

    // 获取专栏标题
    let column_name = await page.evaluate(elem_name => {
        return $(elem_name).next().text();
    }, settings["elem.1.专栏标题标签"]);

    // 不断下拉 取得所有评论
    await scroll_to_bottom(page);

    await page.screenshot({path: "base_page.2.png", fullPage: true, format: "A4"});

    // 等待专栏文章接口返回
    console.log("waiting for article_list");
    while(!article_list_ok) {
        console.log(".");
        await sleep(2);
    }
    console.log("Got article_list ok! Total count:", article_list.length);

    // 开始遍历专栏下的所有文章
    for( let i = 0 ; i < article_list.length ; i++ ) {
        let item = article_list[i];
        item["chapter_name"] = chapter_map[item["chapter_id"]];
    }
    console.log(article_list);

    await page.screenshot({path: "base_page.3.png", fullPage: true, format: "A4"});

    console.log("ALL check passed! You can start working now!");

    for( let i = 0 ; i < article_list.length ; i++ ) {
        let item = article_list[i];
        if(item.id < 40092) {
            continue;
        }
        await (async (item) => {

            const page = await browser.newPage();
            await page.setUserAgent("user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36");
            await page.setRequestInterception(true);

            const working_page = `${settings["page_base"]}${item["id"]}`;
            console.log("working on working_page:", working_page);

            const rand_str = await ppt_insert_jquery.insert_jquery_0(page);
            await page.goto(working_page, {waitUntil: "networkidle0"});
            await ppt_insert_jquery.insert_jquery_1(page, rand_str);

            await sleep(6);

            await page.screenshot({path: "base_page.ing.png", fullPage: true, format: "A4"});

            // 点击沉浸模式
            await valid_deepin_exists(page);

            // 不断下拉 取得所有评论
            await scroll_to_bottom(page);

            let info = {
                "author_name": item["author_name"],
                "column_name": column_name,
                "chapter_id": item["chapter_id"],
                "chapter_name": item["chapter_name"],
                "article_id": item["id"],
                "article_title": item["article_title"],
            }

            const pdf_filename = `${info.author_name}.${info.column_name}/${info.chapter_id}.${info.chapter_name} - ${info.article_id}.${info.article_title}.pdf`;
            
            console.log("pdf_filename:", pdf_filename);
            await fse_create_file(pdf_filename);

            // 额外等待3秒
            await sleep(3);

            await page.emulateMedia("screen");
            await page.pdf({
                path: pdf_filename,
                format: "A4",
                printBackground: true,
                displayHeaderFooter: false,
            });
            // await page.screenshot({path: pdf_filename, fullPage: true});

            await page.close();

        })(item);
    }

    await page.close();
    await browser.close();

})();

