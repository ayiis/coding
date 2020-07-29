
module.exports = {
    sleep: async function(sec) {
        // 暂停 ? 秒
        return new Promise(resolve => setTimeout(resolve, 1000 * sec));
    },
    last_item_of_array: function(array) {
        // 获取列表最后一个元素
        return array.length ? array[array.length - 1] : undefined;
    },
    get_type: function(o) {
        // 获取object的类型
        return Object.prototype.toString.call(o).match(/\w+/g)[1];
    },
    valid_http_type: function(url) {
        // 验证一个字符串是否URL，HTTPS返回1，HTTP返回0
        if (url.toLowerCase().startsWith("https://")) {
            return 1;
        } else if (url.toLowerCase().startsWith("http://")) {
            return 0;
        } else {
            return -1;
        }
    },
    same_val_counter: function(stop_time) {
        /*
            初始化一个计数器，当连续 stop_time 次传入一样的数值时，计数器终止，返回 true
        */
        let now_time = 0;
        let now_value = undefined;
        return function(current_value) {
            if (now_value == current_value) {
                now_time = now_time + 1;
            } else {
                now_time = 0;
                now_value = current_value;
            }
            return now_time == stop_time;
        }
    },
    async_retry_until_times: async function(func, times, sleep_time) {
        let result;
        times = times || 3;
        sleep_time = sleep_time || 3;

        // 失败重试
        for(let i = 0; i < times; i++) {
            try {
                result = await func();
                break;
            } catch (err) {
                console.log("retry:", err);
                await this.sleep(sleep_time);
            }
        }

        return result;
    },
}
