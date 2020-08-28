;(() => {
    let e = document.createElement("img");
    e.hidden = "true";
    document.body.appendChild(e);
    // 利用 img 的 src 标签，每 60 秒发送一次请求到当前页面
    window.setInterval(() => { 
        e.src = window.location.href;
    }, 60000);
})();
