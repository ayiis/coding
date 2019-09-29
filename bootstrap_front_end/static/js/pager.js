'use strict';

window.pager = {
    init_pagination: function(args) {
        // 初始化 分页控件, 一个页面可以使用多个
        var self = this;
        var this_pager = {
            "ele": args.ele,
            "callback": args.callback,

            // 默认值
            "total_count": 0,   // 如果没有返回，默认 0 条结果
            "page_index": 1,    // 默认第 1 页
            "page_size": args.page_size || 25,    // 默认 25 条
            "total_show": args.total_show || 7,    // 默认显示 7 个翻页按钮
        };
        for(var e in self) {
            this_pager[e] = self[e];
        }

        this_pager.ele.empty().append('<nav><ul class="pagination"></ul><ul class="pagination"></ul></nav>');
        this_pager.pagination_ele = this_pager.ele.find('.pagination:eq(0)');
        this_pager.pagination_jump = this_pager.ele.find('.pagination:eq(1)');

        this_pager.ele.on('click', 'a', function() {
            var page_index = Number($(this).attr('val')) || 1;
            this_pager.callback && this_pager.callback(page_index);
            return false;
        });
        this_pager.ele.on('keydown', '.page-jump', function(event) {
            if(event.keyCode == 13) {
                var pageno = $(this).val();
                pageno = Number(pageno) || 1;
                this_pager.callback(pageno);
                return false;
            }
        });

        return this_pager;
    },
    init_document_listener: function() {
        var self = this;
        $(document).keydown(function (event) {
            event = event || window.event;
            if(!self.callback) {
                return;
            }
            switch(event.keyCode) {
                case 37: self.callback(self.page_index - 1); break; // LEFT
                // case 38: x = x - 10; $("selector").css("top", x + "px"); break;  // UP
                case 39: self.callback(self.page_index + 1); break;    // RIGHT
                // case 40: x = x + 10; $("selector").css("top", x + "px"); break;  // DOWN
                // case 13: x = x + 10; $("selector").css("top", x + "px"); break;  // ENTER
                default: break;
            }
        });
    },
    touch_pagination: function(total_count, page_index) {
        var self = this;
        self.total_count = total_count || self.total_count;
        self.page_index  = page_index  || self.page_index;
        var pagination_setting = self.cal_pagination_page(
            self.total_count,
            self.page_index
        );
        var html_list = [];
        for( var i = 0 ; i < pagination_setting.length ; i++ ) {
            var li_string = '';
            var val = pagination_setting[i];
            if (pagination_setting[i] == '') {
                li_string = '<li><span style="padding:16px;background-color:#eee"> </span></li>';
            } else if (i == 0) {
                li_string = '<li><a href="#" val="' + val + '"> ' + val + ' « </a></li>';
            } else if (i == pagination_setting.length - 1) {
                li_string = '<li><a href="#" val="' + val + '"> » ' + val + ' </a></li>';
            } else if (pagination_setting[i] == self.page_index) {
                li_string = '<li class="active"><a href="#" val="' + val + '"> ' + val + ' </a></li>';
            } else {
                li_string = '<li><a href="#" val="' + val + '"> ' + val + ' </a></li>';
            }
            html_list.push(li_string);
        }
        self.pagination_ele.empty().append(html_list.join(""));
        self.pagination_jump.empty().append([
            '<li><input style="width:32px;height:34px;margin-left:16px;text-align:center;border:1px solid #ddd;border-radius:4px;float:left;" class="page-jump" placeholder="GO"/></li>',
            '<li><div style="margin-left:16px;float:left;color:#999;height:34px;"><div style="position:relative;margin:0px;bottom:-10px;">' + self.total_count + ' 条记录</div></div></li>',
        ]);
        self.window_scroll_top();
    },
    cal_pagination_page: function(total_count, page_index) {
        var self = this;
        var first_page = 1;
        var last_page = Math.ceil(total_count / self.page_size);
        page_index = Math.min(page_index, last_page);
        page_index = Math.max(page_index, first_page);
        var start_page = page_index - parseInt(self.total_show / 2);
        var end_page = page_index + Math.round(self.total_show / 2);

        var page_content = [first_page];
        for( var i = start_page; i <= page_index; i++ ) {
            page_content.push(i < first_page ? "" : i );
        }
        for( var i = page_index + 1; i < end_page; i++ ) {
            page_content.push(i > last_page ? "" : i);
        }
        page_content.push(last_page);
        return page_content;
    },
    window_scroll_top: function() {
        $(window).scrollTop(0);
    },
};
