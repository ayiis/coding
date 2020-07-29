const tool = require("./tool.js");

async function scroll_to_bottom_by_element(page, max_try, wait_time) {
    /*
        流式加载的情况，下滑到底部触发流式加载
        找到页面里高度最高的元素，下滑到它的底部
        适用于内容元素高度最高，且设置了 position:absolute 的页面(导致无法计算body高度)
            - 此时 chrome 不能正确识别页面高度，无法打印全页无法截图全页

        适用于:
            ✅滚屏 ✅高度 https://time.geekbang.org/
            ✅滚屏 ✅高度 https://readhub.cn/topics
    */
    max_try = max_try || 20;
    wait_time = wait_time || 2;
    let svc = tool.same_val_counter(3);
    let max_height = 0;
    for(let i = 0; i < max_try; i++ ) {

        max_height = await page.evaluate(() => {
            let max_ele = document.body;
            let max_height = $(document.body).height();
            $("div:visible").each(function(i, ele) {
                let height = $(ele).height() || 0;
                if (height > max_height) {
                    max_ele = ele;
                    max_height = height;
                }
            });
            max_ele.scrollIntoView(true, {behavior: "smooth"});
            setTimeout(function() {
                max_ele.scrollIntoView(false, {behavior: "smooth"});
            }, 200);
            return max_height;
        });

        console.log("Now height:", max_height);
        if(svc(max_height)) {
            break;
        }

        await tool.sleep(wait_time);
    }
    return max_height;
}

async function scroll_to_bottom_by_body(page, max_try, wait_time) {
    /*
        流式加载的情况，下滑到底部触发流式加载
        计算 $(document).height()，直接用jquery的动画拉到底部
        适用于可以直接计算 body高度 的页面

        适用于:
            ✅滚屏 ✅高度 https://time.geekbang.org/
            ✖️滚屏 ✖️高度 https://readhub.cn/topics
    */
    max_try = max_try || 20;
    wait_time = wait_time || 2;
    let max_height = 0;
    let svc = tool.same_val_counter(3);
    for(let i = 0; i < max_try; i++ ) {
        max_height = await page.evaluate(() => {
            $("html, body").animate({ scrollTop: 0}, 100);
            setTimeout(function() {
                $("html, body").animate({ scrollTop: $(document.body).height()}, 100);
            }, 100);
            return $(document).height();
        });

        console.log("Now height:", max_height);
        if(svc(max_height)) {
            break;
        }

        await tool.sleep(wait_time);
    }
    return max_height;
}

async function scroll_to_bottom_by_keyboard(page, max_try, wait_time) {
    /*
        降维打击：模拟键盘快捷键操作
        TODO: 
            缺点：无法准确计算页面 window 的高度
            见：https://bugs.chromium.org/p/chromium/issues/detail?id=34224

        适用于:
            ✅滚屏 ✅高度 https://time.geekbang.org/
            ✅滚屏 ✖️高度 https://readhub.cn/topics
    */
    max_try = max_try || 20;
    wait_time = wait_time || 2;
    let svc = tool.same_val_counter(3);
    let max_height = 0;
    for(let i = 0; i < max_try; i++ ) {

        await page.keyboard.press("End");
        // await page.keyboard.press("PageDown");
        let max_height = await page.evaluate(() => {
            return $(document).height();
        });

        console.log("Now height:", max_height);
        if(svc(max_height)) {
            break;
        }

        await tool.sleep(wait_time);
    }
    return max_height;
}

module.exports = {
    "scroll_to_bottom_by_element": scroll_to_bottom_by_element,
    "scroll_to_bottom_by_body": scroll_to_bottom_by_body,
    "scroll_to_bottom_by_keyboard": scroll_to_bottom_by_keyboard,
    "scroll_to_bottom": scroll_to_bottom_by_element,
}
