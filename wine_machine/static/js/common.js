'use strict';

window.common = {
    record_page_url: "https://127.0.0.1:8082/record/page",
    record_input_count: 1,
    init_pagination: function(ele, callback) {
        var self = this;
        ele.empty().append('<nav><ul class="pagination"></ul></nav>');
        ele.on('click', 'a', function() {
            var page_index = Number($(this).attr('val')) || 1;
            callback && callback(page_index);
            return false;
        });
        ele.on('keydown', '.page-jump', function(event) {
            if(event.keyCode == 13) {
                var pageno = $(this).val();
                pageno = Number(pageno) || 1;
                self.pagination.callback(pageno);
            }
        });
        self.pagination_ele = ele.find('.pagination');
        self.pagination = {
            "callback": callback,
        };
        self.init_document_listener();
    },
    init_document_listener: function() {
        var self = this;
        $(document).keydown(function (event) {
            event= event || window.event;
            switch(event.keyCode) {
                case 37: self.pagination.callback(self.pagination.page_index - 1); break; // LEFT
                // case 38: x = x - 10; $("selector").css("top", x + "px"); break;  // UP
                case 39: self.pagination.callback(self.pagination.page_index + 1); break;    // RIGHT
                // case 40: x = x + 10; $("selector").css("top", x + "px"); break;  // DOWN
                // case 13: x = x + 10; $("selector").css("top", x + "px"); break;  // ENTER
                default: break;
            }
        });
    },
    touch_pagination: function(total_count, page_index, page_size, total_show) {
        var self = this;
        total_count = total_count || 1;
        page_index = page_index || 1;
        page_size = page_size || 25;
        total_show = total_show || 7;
        self.pagination.total_count = total_count;
        self.pagination.page_index = page_index;
        self.pagination.page_size = page_size;
        self.pagination.total_show = total_show;
        var pagination_setting = self.cal_pagination_page(total_count, page_index, page_size, total_show);
        var html_list = [];
        for ( var i = 0 ; i < pagination_setting.length ; i++ ) {
            var li_string = '';
            var val = pagination_setting[i];
            if (pagination_setting[i] == '') {
                li_string = '<li class="page-item disabled"><span style="padding:16px;"> </span></li>';
            } else if (i == 0) {
                li_string = '<li class="page-item"><a class="page-link" href="#" val="' + val + '"> ' + val + ' « </a></li>';
            } else if (i == pagination_setting.length - 1) {
                li_string = '<li class="page-item"><a class="page-link" href="#" val="' + val + '"> » ' + val + ' </a></li>';
            } else if (pagination_setting[i] == page_index) {
                li_string = '<li class="page-item"><span style="font-weight:bold;color:#1b69b6;"> ' + val + ' </span></li>';
            } else {
                li_string = '<li class="page-item"><a class="page-link" href="#" val="' + val + '"> ' + val + ' </a></li>';
            }
            html_list.push(li_string);
        }
        html_list.push('<li class="page-item disabled"><input style="width:32px;height:32px;margin-left:16px;text-align:center;" class="page-jump" placeholder="GO"/></li>');
        self.pagination_ele.empty().append(html_list.join(""));
        self.window_scroll_top();
    },
    cal_pagination_page: function(total_count, page_index, page_size, total_show) {
        var first_page = 1;
        var last_page = Math.ceil(total_count / page_size);
        page_index = Math.min(page_index, last_page);
        page_index = Math.max(page_index, first_page);
        var start_page = page_index - parseInt(total_show / 2);
        var end_page = page_index + Math.round(total_show / 2);

        var page_content = [first_page];
        for(var i = start_page; i <= page_index; i++){
            page_content.push(i < first_page ? "" : i );
        }
        for(var i = page_index + 1; i < end_page; i++){
            page_content.push(i > last_page ? "" : i);
        }
        page_content.push(last_page);
        return page_content;
    },
    bs_modal_message: function(message, title, callback) {
        var modal_html = [
            '<div class="modal" tabindex="-1" role="dialog" id="bs_modal_message">',
            '<div class="modal-dialog" role="document">',
            '<div class="modal-content">',
            '<div class="modal-header">',
            '<h5 class="modal-title">', title || '提示', '</h5>',
            '<button type="button" class="close" data-dismiss="modal" aria-label="Close">',
            '<span aria-hidden="true">&times;</span>',
            '</button>',
            '</div>',
            '<div class="modal-body">',
            '<p>', message, '</p>',
            '</div>',
            '<div class="modal-footer">',
            '<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>',
            '</div>',
            '</div>',
            '</div>',
            '</div>',
        ].join('');
        var $bs_modal_message = $('#bs_modal_message');
        if($bs_modal_message.length > 0) {
            $bs_modal_message.modal('hide');
            $bs_modal_message.remove();
        }
        $(document.body).append(modal_html);
        $bs_modal_message = $('#bs_modal_message');
        $bs_modal_message.on('hide.bs.modal', function (event) {
            $bs_modal_message.remove();
            if (callback) callback();
        });
        // change the z_index to cover old modal
        var max_z_index = 1040;
        if( $('body>.modal-backdrop:last').length > 0) {
            var old_max_z_index = $('body>.modal-backdrop:last').css('z-index');
            old_max_z_index = parseInt(old_max_z_index);
            if (old_max_z_index) {
                max_z_index = Math.max(max_z_index, old_max_z_index);
            }
        }
        $bs_modal_message.modal('show');
        $('body>.modal-backdrop:last').css('z-index', max_z_index + 11);
        $bs_modal_message.css('z-index', max_z_index + 12);
    },
    bs_modal_confirm: function(message, title, yes_callback, no_callback) {
        var modal_html = [
            '<div class="modal" tabindex="-1" role="dialog" id="bs_modal_confirm">',
            '<div class="modal-dialog" role="document">',
            '<div class="modal-content">',
            '<div class="modal-header">',
            '<h5 class="modal-title">', title || '确认', '</h5>',
            '<button type="button" class="close" data-dismiss="modal" aria-label="Close">',
            '<span aria-hidden="true">&times;</span>',
            '</button>',
            '</div>',
            '<div class="modal-body">',
            '<p>', message, '</p>',
            '</div>',
            '<div class="modal-footer">',
            '<button type="button" class="btn btn-danger" tag="yes">确认</button>',
            '<button type="button" class="btn btn-secondary" data-dismiss="modal" tag="no">取消</button>',
            '</div>',
            '</div>',
            '</div>',
            '</div>',
        ].join('');
        var $bs_modal_confirm = $('#bs_modal_confirm');
        if($bs_modal_confirm.length > 0) {
            $bs_modal_confirm.modal('hide');
            $bs_modal_confirm.remove();
        }
        $(document.body).append(modal_html);
        $bs_modal_confirm = $('#bs_modal_confirm');
        $bs_modal_confirm.on('hide.bs.modal', function (event) {
            $bs_modal_confirm.remove();
        });
        $bs_modal_confirm.on('click', 'button[tag="yes"]', function(event) {
            if (yes_callback) yes_callback();
            $bs_modal_confirm.modal('hide');
        });
        // change the z_index to cover old modal
        var max_z_index = 1040;
        if( $('body>.modal-backdrop:last').length > 0) {
            var old_max_z_index = $('body>.modal-backdrop:last').css('z-index');
            old_max_z_index = parseInt(old_max_z_index);
            if (old_max_z_index) {
                max_z_index = Math.max(max_z_index, old_max_z_index);
            }
        }
        $bs_modal_confirm.modal('show');
        $('body>.modal-backdrop:last').css('z-index', max_z_index + 11);
        $bs_modal_confirm.css('z-index', max_z_index + 12);
    },

    add_record_input: function(previous, id, bind_value, has_record) {
        if(previous) {
            if(!bind_value) {
                bind_value = "";
            }
            id = id + '_' + this.record_input_count;
            var record_html = '<a class="btn btn-sm btn-outline-info mr-1 ai-btn" href="#" tag="record_input">录音</a>';
            if(!has_record) {
                record_html = '';
            }
            $(previous).after([
                '<div class="input-group mb-3" tag="dynamic_input_div">',
                    '<div class="input-group-prepend">',
                        '<span class="input-group-text">AI问题:</span>',

                    '</div>',
                    '<input type="text" class="form-control ai-input" id="' + id + '" value="' + bind_value + '">',
                    '<a class="btn btn-sm btn-outline-success mr-1 ai-btn" href="#" tag="add_input">添加</a>',
                    record_html,
                    '<a class="btn btn-sm btn-outline-danger mr-1 ai-btn" href="#" tag="remove_input">删除</a>',
                '</div>'
            ].join(''));
            this.record_input_count++;
        }
    },
    clear_dynamic_div: function() {
        $('div[tag="dynamic_input_div"]').remove();
    },
    format_seconds: function (value) {
        var theTime = parseInt(value);// 秒
        var theTime1 = 0;// 分
        var theTime2 = 0;// 小时
        if (theTime > 60) {
            theTime1 = parseInt(theTime / 60);
            theTime = parseInt(theTime % 60);
            if (theTime1 > 60) {
                theTime2 = parseInt(theTime1 / 60);
                theTime1 = parseInt(theTime1 % 60);
            }
        }
        var result = "" + parseInt(theTime) + "秒";
        if (theTime1 > 0) {
            result = "" + parseInt(theTime1) + "分" + result;
        }
        if (theTime2 > 0) {
            result = "" + parseInt(theTime2) + "小时" + result;
        }
        return result;
    },
    get_query_string: function(name) {
        var result = window.location.search.match(new RegExp("[\?\&]" + name + "=([^\&]+)", "i"));
        if (result == null || result.length < 1) {
            return "";
        }
        return result[1];
    },
    scroll_to_ele: function(container, ele) {
        var $container = $(container);
        var $scrollTo = $(ele);
        // $container.scrollTop($scrollTo.offset().top - $container.offset().top + $container.scrollTop());

        $container.animate({
            "scrollTop": $scrollTo.offset().top - $container.offset().top + $container.scrollTop()
        });
        // container.scrollTop(ele.offset().top - container.offset().top + container.scrollTop());
    },
    window_scroll_top: function(){
        $(window).scrollTop(0);
    }
};


Date.prototype.format = function (format) {
    var o = {
        "M+": this.getMonth() + 1, //month
        "d+": this.getDate(),    //day
        "h+": this.getHours(),   //hour
        "m+": this.getMinutes(), //minute
        "s+": this.getSeconds(), //second
        "q+": Math.floor((this.getMonth() + 3) / 3),  //quarter
        "S": this.getMilliseconds() //millisecond
    }
    if (/(y+)/.test(format)) format = format.replace(RegExp.$1,
        (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o) if (new RegExp("(" + k + ")").test(format))
        format = format.replace(RegExp.$1,
            RegExp.$1.length == 1 ? o[k] :
                ("00" + o[k]).substr(("" + o[k]).length));
    return format;
};


Number.prototype._toFixed = Number.prototype._toFixed || Number.prototype.toFixed;
Number.prototype.toFixed = function(precision) {
    return (+(Math.round(+(this + 'e' + precision)) + 'e' + -precision))._toFixed(precision);
}
