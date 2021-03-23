let max_height = 9999;
let _tmp = [];
try {
    document.getElementsByClassName('simplebar-content').forEach(function(e){_tmp.push(Math.max(e.offsetHeight, e.clientHeight, e.scrollHeight))});
    max_height = Math.max.apply(this, _tmp);
} catch {}
max_height = max_height + 60;
document.getElementById('app').children[0].setAttribute('style', 'height:' + max_height + 'px');



1. 是否需要评论
2. 


