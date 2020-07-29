const puppeteer = require('puppeteer');
const fse = require('fs-extra'); // v 5.0.0
const { URL } = require('url');
const path = require('path');
const mongo = require('mongodb');
const https = require('https');
const fs = require('fs');
/*
   《医学英语高频词汇课：6大常见学科核心词汇》 是App独享的，无法爬取

    分析思路：

        课程列表页：

            获取所有课程的 链接地址
            获取所有课程的 课程名称

        课程页：

            获取本课程下的 章节列表
            点击翻页 并判断是否到了 最后一页
            点击每一个章节 获取视频资源

        视频资源的类型可以分为3种：

            mp4 / ts（原始格式） / ts（aes加密）

            - 针对 mp4

                从 /pcweb/video/play-url 接口获取 mp4 文件链接，直接下载

            - 针对 ts（原始格式）

                从 /pcweb/video/play-url 接口获取 m3u8 文件链接，下载 m3u8
                解析 m3u8 文件，获得所有的 ts 文件片段地址
                下载所有的 ts 文件片段
                拼接 ts 文件为1个 ts 文件

            - 针对 ts（aes加密）
                
                在 ts（原始格式）的步骤的基础上增加：
                从 /webservices/clazz/video/getDK 接口获取 aes 的 KEY，IV统一为 0x0000000000000000
                下载所有的 ts 文件片段，并分别解密所有的 ts 文件片段
                拼接解密后的 ts 文件为1个 ts 文件

        最后使用课程名称和章节名称命名视频文件，完成

*/

// 所有课程信息
const course_data = [{"id":1525,"courseId":3,"courseType":2,"typeAndId":"2_3","courseName":"从零做医学基础科研，小张教你发3分SCI","currentPrice":69800,"listPic":"https://img1.dxycdn.com/2019/1206/996/3383582142142784840-73.png","coverPic":"https://img1.dxycdn.com/2019/1206/627/3383582365481309718-73.png","courseUrl":"https://class.dxy.cn/clazz/course/3","currentPriceYuan":"698"},{"id":1526,"courseId":4,"courseType":2,"typeAndId":"2_4","courseName":"基金标书写作与申报技巧","currentPrice":38800,"listPic":"https://img1.dxycdn.com/2018/0521/326/3278964708124247343-10.png","coverPic":"https://img1.dxycdn.com/2017/0905/923/3231113861379187922-10.jpg","courseUrl":"https://class.dxy.cn/clazz/course/4","currentPriceYuan":"388"},{"id":1539,"courseId":17,"courseType":2,"typeAndId":"2_17","courseName":"Western blot 成功之道","currentPrice":19800,"listPic":"https://img1.dxycdn.com/2019/1206/497/3383607967781318284-73.png","coverPic":"https://img1.dxycdn.com/2019/1206/682/3383607972076115130-73.png","courseUrl":"https://class.dxy.cn/clazz/course/17","currentPriceYuan":"198"},{"id":1546,"courseId":24,"courseType":2,"typeAndId":"2_24","courseName":"STATA 软件在Meta分析中的应用","currentPrice":16800,"listPic":"https://img1.dxycdn.com/2018/0521/979/3278964832678299442-10.png","coverPic":"https://img1.dxycdn.com/2017/1027/986/3240787050879352448-10.png","courseUrl":"https://class.dxy.cn/clazz/course/24","currentPriceYuan":"168"},{"id":1547,"courseId":25,"courseType":2,"typeAndId":"2_25","courseName":"RevMan软件在meta分析中的应用","currentPrice":12800,"listPic":"https://img1.dxycdn.com/2018/0521/217/3278964879922939853-10.png","coverPic":"https://img1.dxycdn.com/2017/1027/445/3240786997192261230-10.png","courseUrl":"https://class.dxy.cn/clazz/course/25","currentPriceYuan":"128"},{"id":1567,"courseId":45,"courseType":2,"typeAndId":"2_45","courseName":"实用数据挖掘，用公开的数据发自己的文章","currentPrice":48800,"listPic":"https://img1.dxycdn.com/2019/1206/460/3383631471989812387-73.png","coverPic":"https://img1.dxycdn.com/2019/1206/575/3383631489169681853-73.png","courseUrl":"https://class.dxy.cn/clazz/course/45","currentPriceYuan":"488"},{"id":1575,"courseId":53,"courseType":2,"typeAndId":"2_53","courseName":"临床研究设计从入门到精通","currentPrice":48800,"listPic":"https://img1.dxycdn.com/2019/1206/268/3383583589546800136-73.png","coverPic":"https://img1.dxycdn.com/2019/1206/035/3383583791410268593-73.png","courseUrl":"https://class.dxy.cn/clazz/course/53","currentPriceYuan":"488"},{"id":1576,"courseId":54,"courseType":2,"typeAndId":"2_54","courseName":"医学统计学从入门到精通","currentPrice":48800,"listPic":"https://img1.dxycdn.com/2019/1206/018/3383584974674001839-73.png","coverPic":"https://img1.dxycdn.com/2019/1206/038/3383584981116452909-73.png","courseUrl":"https://class.dxy.cn/clazz/course/54","currentPriceYuan":"488"},{"id":1642,"courseId":120,"courseType":2,"typeAndId":"2_120","courseName":"零基础统计实战教程","currentPrice":48800,"listPic":"https://img1.dxycdn.com/2019/1206/143/3383637431256673729-73.png","coverPic":"https://img1.dxycdn.com/2020/0313/872/3401794113442776943-73.png","courseUrl":"https://class.dxy.cn/clazz/course/120","currentPriceYuan":"488"},{"id":1679,"courseId":157,"courseType":2,"typeAndId":"2_157","courseName":"从零学GraphPad作图统计：基础篇","currentPrice":28800,"listPic":"https://img1.dxycdn.com/2018/0521/754/3278971657381016521-10.png","coverPic":"https://img1.dxycdn.com/2018/0521/278/3278971657381016513-10.png","courseUrl":"https://class.dxy.cn/clazz/course/157","currentPriceYuan":"288"},{"id":1768,"courseId":246,"courseType":2,"typeAndId":"2_246","courseName":"样本量计算，PASS实战教程","currentPrice":10800,"listPic":"https://img1.dxycdn.com/2018/1221/388/3318638843602933527-10.png","coverPic":"https://img1.dxycdn.com/2018/0925/419/3302525092676113037-10.png","courseUrl":"https://class.dxy.cn/clazz/course/246","currentPriceYuan":"108"},{"id":1828,"courseId":306,"courseType":2,"typeAndId":"2_306","courseName":"中文医学核心期刊论文撰写与投稿技巧","currentPrice":16800,"listPic":"https://img1.dxycdn.com/2019/1206/939/3383579915202186630-73.png","coverPic":"https://img1.dxycdn.com/2019/1206/314/3383579921644637717-73.png","courseUrl":"https://class.dxy.cn/clazz/course/306","currentPriceYuan":"168"},{"id":1835,"courseId":313,"courseType":2,"typeAndId":"2_313","courseName":"科研大咖之路：十分钟医学文献阅读攻略","currentPrice":28800,"listPic":"https://img1.dxycdn.com/2019/1204/942/3383213603883873055-73.png","coverPic":"https://img1.dxycdn.com/2019/1204/419/3383213610326324157-73.png","courseUrl":"https://class.dxy.cn/clazz/course/313","currentPriceYuan":"288"},{"id":1939,"courseId":5,"courseType":5,"typeAndId":"5_5","courseName":"医学英语高频词汇课：6大常见学科核心词汇","currentPrice":8800,"listPic":"https://img1.dxycdn.com/2018/0726/910/3291202446487643459-73.png","coverPic":"https://img1.dxycdn.com/2018/0727/806/3291409959979639218-73.png","courseUrl":"https://class.dxy.cn/audio/5","currentPriceYuan":"88"},{"id":2120,"courseId":424,"courseType":2,"typeAndId":"2_424","courseName":"SCI 论文插图实用制作攻略","currentPrice":28800,"listPic":"https://img1.dxycdn.com/2019/1206/359/3383578570877390568-73.png","coverPic":"https://img1.dxycdn.com/2019/1206/888/3383578577319841671-73.png","courseUrl":"https://class.dxy.cn/clazz/course/424","currentPriceYuan":"288"},{"id":2146,"courseId":443,"courseType":2,"typeAndId":"2_443","courseName":"临床病例报告写作课程","currentPrice":19800,"listPic":"https://img1.dxycdn.com/2019/1029/563/3376590425011367178-73.png","coverPic":"https://img1.dxycdn.com/2019/1115/663/3379731764091566467-73.png","courseUrl":"https://class.dxy.cn/clazz/course/443","currentPriceYuan":"198"},{"id":2424,"courseId":580,"courseType":2,"typeAndId":"2_580","courseName":"Meta 分析从入门到精通","currentPrice":58800,"listPic":"https://img1.dxycdn.com/2020/0318/917/3402738802236866116-73.png","coverPic":"https://img1.dxycdn.com/2020/0318/936/3402738785056996343-73.png","courseUrl":"https://class.dxy.cn/clazz/course/580","currentPriceYuan":"588"}];
// 课程网址的固定后缀
const course_fix = "?sr=22&nm=sylxhy&pd=class";

// 目标资源的请求地址 1    
const target_resource_url = {
    "hostname": "class.dxy.cn",
    "pathname": "/pcweb/video/play-url",
}
// 目标资源的请求地址 2
const target_resource_key_url = {
    "hostname": "class.dxy.cn",
    "pathname": "/webservices/clazz/video/getDK",
}
// 视频保存目录
const download_file_path = "./dxy";

async function sleep(sec) {
    return new Promise(resolve => setTimeout(resolve, 1000*sec));
}

async function fse_create_file(file_name) {
    await fs.ensureFile(file_name);
    // return new Promise(resolve => fse.ensureFile(file_name, resolve));
}

async function download_file(target_url, save_as_name, resolve, reject) {
    try {
        const file_name = `${download_file_path}/${save_as_name}`;
        // console.log("creating file:", file_name);
        await fse_create_file(file_name);
        https.get(target_url, {
            "method": "GET",
            "timeout": 1000 * 60,
            // 构造 http-headers
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6,ja;q=0.5",
                "origin": "https://class.dxy.cn",
                "referer": "https://class.dxy.cn/clazz/course/3?sr=22&nm=sylxhy&pd=class",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            }
        }, (response => {
            const filestream = fs.createWriteStream(file_name);
            response.pipe(filestream);
            filestream.on("finish", function(){
                console.log("Saved", save_as_name);
                resolve();
            });
        }));
    } catch(err) {
        console.log(err);
        reject(err);
    }
}

async function wrap_download_file(target_url, save_as_name) {
  return new Promise((resolve, reject) => download_file(target_url, save_as_name, resolve, reject));
}

async function download_mp4(target_url, resource_name) {
    // 失败重试2次
    for(let t = 0; t < 3; t++) {
        try {
            await wrap_download_file(target_url, resource_name);
            break;
        } catch (err) {
            console.log(err);
            await sleep(3);
        }
    }
}

async function download_m3u8(target_url_m3u8, resource_name) {
    // 新建一个文件夹 将所有ts文件都保存到这个文件夹下 后面再合成
    let m3u8_save_name = `${resource_name}/temp.m3u8`;
    let done_file_mark = `${download_file_path}/${resource_name}/done.temp`;

    let m3u8url = new URL(target_url_m3u8);
    let base_path = `${m3u8url.origin}${m3u8url.pathname.substr(0, m3u8url.pathname.lastIndexOf("/"))}`;

    if (fse.pathExistsSync(done_file_mark)) {
        console.log("[Warning] This lesson already done!");
        return;
    }

    // 下载 m3u8 文件，里面有所有 ts 文件的片段
    let download_m3u8_ok = false;
    for(let t = 0; t < 3; t++) {
        try {
            await wrap_download_file(target_url_m3u8, m3u8_save_name);
            download_m3u8_ok = true;
            break;
        } catch (err) {
            console.log(err);
            await sleep(3);
        }
    }
    write_log(target_url_m3u8, download_m3u8_ok);

    // 读取 m3u8 文件，过滤掉里面的注释 #
    let contents = fse.readFileSync(`${download_file_path}/${m3u8_save_name}`, "utf8");
    contents = contents.split("\n");
    let ts_url_contents = [];
    for(let i = 0; i < contents.length; i++) {
        let content = contents[i]; 
        if(content && content.trim()[0] != "#") {
            ts_url_contents.push(content); 
        }
    }
    console.log("m3u8 contains", ts_url_contents.length, "items");

    // 遍历下载所有的 ts文件片段
    for(let i = 0; i < ts_url_contents.length; i++) {
        let ts_url = `${base_path}/${ts_url_contents[i]}`;
        let ts_url_obj = new URL(ts_url);
        let ts_save_name = `${resource_name}/${ts_url_obj.searchParams.get("start")}.${ts_url_obj.searchParams.get("end")}.ts`;

        let download_ok = false;
        for(let t = 0; t < 2; t++) {
            try {
                console.log(`Getting ${ts_url} to ${ts_save_name}`);
                await wrap_download_file(ts_url, ts_save_name);
                download_ok = true;
                break;
            } catch (err) {
                console.log(err);
                await sleep(3);
            }
        }
        write_log(ts_url, download_ok);
        // break;
    }
    console.log("All is done from m3u8");

    await fse_create_file(done_file_mark);
}


function write_log(msg, success=true) {
    const log_head = success ? "[success]" : "[fail]";
    fse.appendFileSync("log_file.txt", `${log_head} ${msg}\n`, (err) => {
        if (err) throw err;
    });
}

function write_file(filename, content) {
    fse.outputFileSync(`${download_file_path}/${filename}`, content, (err) => {
        if (err) throw err;
    });
}

async function insert_jquery(page, rand_str) {

    // 动态插入 jquery
    const add_script = await page.evaluate(rand_str => {
        document.body.appendChild(document.createElement("script")).setAttribute("src", rand_str);
        return true;
    }, rand_str);

    if (add_script) {
        await page.waitForResponse(response => {
            // 等到 jquery 加载完毕返回 true 时，方法执行完毕
            return response.request().url().endsWith(rand_str);
        });
    }
    console.log("jQuery inserted ok!");

    // 检查 jquery 是否已经生效
    await page.waitForFunction("!!window.jQuery");
    console.log("jQuery works good!");
}

;(async () => {

    // 配置 puppeteer 使用固定的 Chrome，预先输入登录信息
    const browser = await puppeteer.launch({
        executablePath: "/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome",
        userDataDir: "/tmp/tmp",
        // headless: true,
        headless: false,
        // devtools: false,
        devtools: true,
        slowMo: 20,
        defaultViewport: null
    });

    const context = browser.defaultBrowserContext();
    await context.clearPermissionOverrides();

    let lesson_continue_page = 1;
    let lesson_continue_index = 1;

    // 从中断的地方继续爬
    // lesson_continue_page = 2;
    // lesson_continue_index = 4;

    for(let course_index = 0; course_index < course_data.length; course_index++) {

        // 起始页面
        let this_course = course_data[course_index];

        // // 从中断的地方继续爬
        // // ！未完成下载的，需要先删除原来下载了的文件，因为可能会重新划定范围
        // if( this_course["id"] < 1679) {
        //     continue;
        // }
        let first_page = `${this_course["courseUrl"]}${course_fix}`;
        let base_folder_name = this_course["courseName"];

        write_log(`[ON] ${base_folder_name}`, true);
        console.log(`[ON] ${first_page}`);
        console.log(`[ON] ${base_folder_name}`, "start from:", lesson_continue_page);

        await fse_create_file(`${download_file_path}/${base_folder_name}/empty.tmp`);
        await sleep(3);

        // 每个课程使用新的作用域
        await (async (first_page, base_folder_name, lesson_continue_page) => {

            let folder_name = `${base_folder_name}`;    // 共享
            base_folder_name = base_folder_name.replace(/\//g, "_");

            const page = await browser.newPage();
            const rand_str = `/${Math.random().toString(36)}`;  // 插入jQuery
            let got_mp4 = false;                        // 共享
            let got_m3u8 = false;                        // 共享
            let got_m3u8_key = false;                   // 共享
            let lesson_download_finish = false;         // 共享
            let lesson_page = 1;

            await page.setRequestInterception(true);
            page.on('request', async(interceptedRequest) => {
                const url = new URL(interceptedRequest.url());
                if (url.pathname && url.pathname[0] == "/") {
                    if (url.pathname.endsWith(".mp4") || url.pathname.endsWith(".ts")) {
                        console.log("<BLOCK>", url.hostname, url.pathname);
                        // return interceptedRequest.abort();
                        // 留着让它一直请求
                        return;
                    } else {
                        // console.log(url.hostname, " -- " , url.pathname);
                    }
                }
                if (url.pathname === rand_str) {
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

            page.on('response', async (response) => {
                const url = new URL(response.url());
                if (url.protocol == "data:" || url.protocol == "blob:") {
                    console.log(`[skip] ${url.protocol} len: ${url.pathname.length}`);
                    return;
                }
                if (response.status() !== 200){
                    return;
                }
                if (
                    url.hostname == target_resource_url["hostname"] 
                    && url.pathname == target_resource_url["pathname"]
                ) {
                    let play_url_content = await response.buffer();
                    play_url_content = play_url_content.toString("utf8");
                    console.log("Got content:", play_url_content);
                    play_url_content = JSON.parse(play_url_content);

                    let resource_url = play_url_content["data"];
                    let resource_url_obj = new URL(resource_url);
                    console.log(`Downloading ${resource_url}`);
                    if (resource_url_obj.pathname.endsWith(".mp4")) {
                        // mp4 文件直接下载
                        if (got_mp4 == true) {
                            console.log("[SKIP] MP4 already got! Skip this..");
                            return;
                        } else {
                            console.log("Got mp4!");
                            got_mp4 = true;
                            await download_mp4(resource_url, `${folder_name}/temp.mp4`);
                            lesson_download_finish = true;
                        }
                    } else if (resource_url_obj.pathname.endsWith(".m3u8")) {
                        // m3u8 文件解析后下载
                        console.log("Sleep for 5 seconds to wait if there is mp4...");
                        // 如果有mp4文件，直接下载mp4，跳过ts文件
                        await sleep(5);
                        if (got_mp4 == true) {
                            console.log("[SKIP] Got mp4! Skip ts file");
                            return;
                        } else {
                            if (got_m3u8 == true) {
                                console.log("[SKIP] M3u8 already got! Skip this..");
                                return;
                            } else {
                                got_m3u8 = true;
                                await download_m3u8(resource_url, folder_name);
                                lesson_download_finish = true;
                            }
                        }
                    }
                    return;
                } else if ( 
                    // m3u8 的 key，所有ts片段都是使用一样的 key
                    // 有一些ts视频是无 key 的
                    url.hostname == target_resource_key_url["hostname"]
                    && url.pathname == target_resource_key_url["pathname"]
                ) {
                    let key_content = await response.buffer();
                    write_file(`${folder_name}/temp.key`, key_content);
                    return;
                }
            });

            // 打开页面 等待网络请求完成
            await page.goto(first_page, {waitUntil: "networkidle2"});

            // 强制插入 jQuery
            await insert_jquery(page, rand_str);

            // 标记父节点
            await sleep(1);
            const _SET_COURSE_LIST_ID_ = await page.evaluate(() => {
                $("#intro").parent().parent().parent().attr("id", "aysl");
                return !!$("#aysl").length;
            });
            if(!_SET_COURSE_LIST_ID_) {
                console.log("[ERROR] this course cannot be play:", base_folder_name);
                write_log("[ERROR] this course " + base_folder_name +" cannot be play", false);
                return;
            }

            // 点击课程目录 获取课程下所有章节
            await sleep(1);
            const _CLICK_COURSE_LIST_ = await page.evaluate(() => {
                return $("#aysl").find("div>span").filter(function() {
                    return $(this).text().trim() == "课程目录";
                }).click();
            });

            // 记录是否已经翻页到了最后一页
            let last_page_name_hash = "";
            for(let lesson_page_count = 0; lesson_page_count < 99; lesson_page_count++ ) {

                await sleep(2);
                let page_name_hash = await page.evaluate(() => {
                    return $("#aysl").find("h1").next().text().trim();
                });

                console.log("[info] got page name:", page_name_hash);

                if (last_page_name_hash && last_page_name_hash == page_name_hash) {
                    console.log("[info] reach the end of course! At page:", lesson_page);
                    break;
                } else {
                    last_page_name_hash = page_name_hash;
                }

                let lesson_length = await page.evaluate(() => {
                    return $("#aysl").find("h1").next().find(">div").length;
                });
                if (lesson_length > 5) {
                    console.log("[        ]\r\n[warnning] lesson length is:", lesson_length);
                } else {
                    console.log("[info] lesson length is:", lesson_length);
                }

                // 从中断页面继续
                if (lesson_continue_page <= lesson_page) {

                    // 重置 页面计数器
                    lesson_continue_page = 1;

                    // 遍历本页所有章节 一般是5个
                    for(let lesson_index = 0; lesson_index < lesson_length; lesson_index++ ) {
                        if (lesson_index < lesson_continue_index - 1) {
                            continue;
                        } else {
                            // 重置 章节计数器
                            lesson_continue_index = 1;
                        }

                        // 重置下载标志
                        got_m3u8_key = false;
                        lesson_download_finish = false;
                        got_mp4 = false;
                        got_m3u8 = false;

                        await (async function(lesson_index) {
                            let lesson_name = await page.evaluate((lesson_index) => {
                                console.log(lesson_index);
                                return $("#aysl").find("h1").next().find(">div").eq(lesson_index).find("p").text();
                            }, (lesson_index));
                            lesson_name = lesson_name ? lesson_name.trim() : null;
                            if(!lesson_name) {
                                console.log("[warnning] lesson index", lesson_index, "has no data");
                                return;
                            }

                            // 注意：此处修改的是上一级作用域的变量
                            folder_name = `${base_folder_name}/${lesson_name}`;
                            console.log("[info] save to", folder_name);

                            // 点击章节（选课）获取视频
                            // 此处将触发网络请求 触发 request 和 respose 事件
                            const _CLICK_COURSE_ = await page.evaluate(lesson_index => {
                                $("#aysl").find("h1").next().find(">div").eq(lesson_index).click();
                            }, lesson_index);
                            await sleep(2);
                        })(lesson_index);

                        // 等待本章节下载完成
                        while(lesson_download_finish == false) {
                            await sleep(2);
                        }

                        // 等待，避免操作太频繁
                        await sleep(5);
                    }
                }

                // 点击下一页
                const _CLICK_NEXT_PAGE_ = await page.evaluate(() => {
                    $("#aysl").find(">div:last>div:last>div:last>span:last").click();
                });
                lesson_page = lesson_page + 1;
                await sleep(2);

            }

            console.log("[Done] This course is saved to:", base_folder_name);

        })(first_page, base_folder_name, lesson_continue_page);

        // 等待，避免操作太频繁
        console.log("[Done] 9 seconds to open new page");
        await sleep(9);
    }
    console.log("[Done] All done.");

})();

/*

    course 系列课程
    lesson 课程下的章节

    document.body.appendChild(document.createElement("script")).setAttribute('src', 'https://code.jquery.com/jquery-3.3.1.min.js');
    $("#intro").parent().parent().parent().attr("id", "aysl");
*/
