const puppeteer = require('puppeteer');
const fse = require('fs-extra'); // v 5.0.0
const { URL } = require('url');
const path = require('path');
const mongo = require('mongodb');
const https = require('https');
const fs = require('fs');
const ppt_request_intercept = require('../common/request_intercept.js');
const ppt_tool = require('../common/tool.js');

/*

✅ 00 打开 chromium 保存 cookie

✅ 0. 打开起始页面
    https://kaiwu.lagou.com/course/courseInfo.htm?courseId=64
    https://kaiwu.lagou.com/course/courseInfo.htm?courseId=43

        - 获取课程下的所有章节

✅ 2. 打开文章页面

✅ 3. 去除所有干扰样式

✅ 4. 计算并补充 height

✅ 5. 保存为pdf

    64.云原生微服务架构实战精讲/429.模块一：架构与背景知识 - 1804.第01讲：什么是微服务架构.pdf
    {course_id}.{course_name}/{section_id}.{section_name} - {lesson_id}.{lesson_name}.pdf


遇到的问题：

    376.模块一：磨刀不误砍柴工：基础篇 - 1587.第02讲：通过案例全面比较传统测试与敏捷测试
        ==> error.pdf

    图片扰乱了页面高度，在pdf计算的时候不能准确计算

    https://kaiwu.lagou.com/course/courseInfo.htm?courseId=455#/detail/pc?id=4571&scrollTop=5468

*/
const settings = {

    "start_page": "https://kaiwu.lagou.com/",
    "course_id_list": [377],    // 43, 64

    "page_base_course": "https://kaiwu.lagou.com/course/courseInfo.htm?courseId=${course_id}",
    "page_base_lesson": "https://kaiwu.lagou.com/course/courseInfo.htm?courseId=${course_id}#/detail/pc?id=${lesson_id}",
}

// 目标资源的请求地址 - 专栏文章列表接口
const target_url_article_list = {
    "hostname": "gate.lagou.com",
    "pathname": "/v1/neirong/kaiwu/getCourseLessons",
}

async function fse_create_file(file_name) {
    return new Promise(resolve => fse.ensureFile(file_name, resolve));
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

    // // 进入首页，目测一下有没有发生异常
    // const page = await browser.newPage();
    // await page.setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36");
    // await page.goto(settings["start_page"], {waitUntil: "networkidle0"});
    // await ppt_tool.sleep(999999);

    for(let i = 0; i < settings.course_id_list.length ; i++ ) {

        // 0. 打开起始页面
        const page = await browser.newPage();
        await page.setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36");

        // 文章列表保存到此变量
        let article_list = [];
        let article_list_ok = false;

        // 监听文章列表接口
        page.on("response", async (response) => {
            const url = new URL(response.url());
            if (response.status() !== 200) {
                return;
            }
            // 文章列表信息 - 接口解析
            else if (
                url.hostname == target_url_article_list["hostname"] 
                && url.pathname == target_url_article_list["pathname"]
            ) {
                if (article_list_ok) {
                    return;
                }
                let article_list_content = await response.buffer();
                article_list_content = article_list_content.toString("utf8");
                console.log("Got target_url_article_list data:", article_list_content.length);
                article_list_content = JSON.parse(article_list_content);
                console.log(`state: ${article_list_content["state"]}, message: ${article_list_content["message"]}`);
                console.log(article_list_content["content"]);
                article_list_content["content"]["courseSectionList"].forEach((section) => {
                    section["courseLessons"].forEach((lesson) => {
                        // 只取已经发布的文章
                        if(lesson.status.toUpperCase() == "RELEASE") {
                            article_list.push({
                                "section_id": section.id,
                                "section_name": section.sectionName,

                                "lesson_id": lesson.id,
                                "lesson_name": lesson.theme,
                            });
                        }
                    });
                });
                article_list_ok = true;
            }
        });

        let course_id = settings.course_id_list[i];

        // 进入 专栏
        let course_url = settings["page_base_course"].replace("${course_id}", course_id);
        console.log("Working on course:", course_id);

        await page.goto(course_url, {waitUntil: "networkidle0"});
        await ppt_request_intercept.insert_jquery(page);

        await page.screenshot({path: "base_page.0.png", fullPage: true, format: "A4"});

        // 额外等待6秒
        await ppt_tool.sleep(6);
        await page.screenshot({path: "base_page.1.png", fullPage: true, format: "A4"});

        // 获取专栏标题
        let course_name = await page.evaluate(() => {
            return $(".intro-content>.conent-wrap>.name").text().trim();
        });

        await page.screenshot({path: "base_page.2.png", fullPage: true, format: "A4"});

        // 等待专栏文章接口返回
        console.log("Waiting for article_list of", course_name, "..");
        while(!article_list_ok) {
            console.log(".");
            await ppt_tool.sleep(2);
        }
        console.log("Got article_list ok! Total count:", article_list.length);

        await page.screenshot({path: "base_page.3.png", fullPage: true, format: "A4"});
        console.log("ALL check passed! You start working now!");

        // 开始遍历专栏下的所有文章
        for( let i = 0 ; i < article_list.length ; i++ ) {
            let item = article_list[i];
            // if(item.id < 40092) {
            //     continue;
            // }
            await (async (item) => {

                const page = await browser.newPage();
                await page.setUserAgent("user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36");

                const working_page = settings["page_base_lesson"].replace("${course_id}", course_id).replace("${lesson_id}", item.lesson_id);
                console.log("working on working_page:", working_page);

                await page.goto(working_page, {waitUntil: "networkidle0"});
                await ppt_request_intercept.insert_jquery(page);

                await ppt_tool.sleep(5);

                console.log("wait for [write messaage button]..");
                await page.waitForFunction("$('.message-topic-write.pointer').length === 1");

                await ppt_tool.sleep(2);

                // await page.screenshot({path: "working_page.0.png", fullPage: true, format: "A4"});
                console.log("fixed style..");

                // 去除所有干扰样式
                await page.evaluate(() => {
                    $(".item-wrap.inline-block.catalog").click();
                });
                await ppt_tool.sleep(2);

                // 去除所有干扰样式
                await page.evaluate(() => {
                    $(".wrap.pc-header").remove();
                    $(".pub-header").remove();
                    // $(".buy-tips-wrap").remove();
                });

                // 计算并补充 height
                let add_height = await page.evaluate(() => {
                    let height = $(".main-wrap").height();
                    let add_height = height + (height / 800) * 170;

                    $(".right-content-wrap").css({
                        "height": add_height + 50,
                    });
                    return add_height;
                });
                await ppt_tool.sleep(2);
                console.log("Fixed height:", add_height);

                let tmp_filename = `${item.section_id}.${item.section_name} - ${item.lesson_id}.${item.lesson_name}`;
                tmp_filename = tmp_filename.replace(/\//g, " ");
                const pdf_filename = `${course_id}.${course_name}/${tmp_filename}.pdf`;

                console.log("pdf_filename:", pdf_filename);
                await fse_create_file(pdf_filename);

                // 额外等待3秒
                await ppt_tool.sleep(3);

                await page.emulateMedia("print");   // screen
                await page.screenshot({path: pdf_filename + ".png", fullPage: true});
                await page.pdf({
                    path: pdf_filename,
                    format: "A4",
                    printBackground: true,
                    displayHeaderFooter: false,
                    // height: 139 + DELTA + 3 + 3 + 'mm', // Additional page margins of 3mm
                    // width: 550 + DELTA + 3 + 3 + 'mm', // ·Additional page margins of 3mm
                    // margin: {
                    //     top: 0,
                    //     right: 0,
                    //     bottom: 0,
                    //     left: 0,
                    // },
                });


            })(item);

            await ppt_tool.sleep(3);
        }

        await page.close();
        await ppt_tool.sleep(5);

    }
    await browser.close();

})();



