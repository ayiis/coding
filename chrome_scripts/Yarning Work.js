;(()=>{
    // 插入 jQuery
    if(!window.jQuery) {
        document.body.appendChild(document.createElement("script")).setAttribute("src", "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js");
    }
    // 等待 jQuery 生效
    let later = (method) => {
        setTimeout(!!window.jQuery ? method : () => { later(method) }, 50);
    }
    // 使用 jQuery
    ;later(() => {
        // 修改页面样式
        $(".sidebar-menu-con,.main-header-con").remove();
        $(".single-page-con").attr("style", "padding:0;margin-top:-100px;");

        // 绑定快捷键 ctrl + enter 查询事件
        $(".ivu-tabs-content .ivu-tabs-content").on("keydown", ".ace_text-input", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.keyCode == 13) {
                $(e.target).closest(".ivu-tabs-tabpane").find(".ivu-btn.ivu-btn-success").click();
                return false;
            }
        });
    });
})();
