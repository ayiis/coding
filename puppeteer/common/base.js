
async function sleep(sec) {
    return new Promise(resolve => setTimeout(resolve, 1000 * sec));
}

function same_val_counter(stop_time) {
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
}

module.exports = {
    "sleep": sleep,
    "same_val_counter": same_val_counter,
}
