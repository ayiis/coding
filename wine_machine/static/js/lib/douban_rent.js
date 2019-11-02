'use strict';

window.douban_rent = {
    init: function() {
        var self = this;
        self.bind_event();
        self.do_search();
    },
    bind_event: function() {
        var self = this;
        $('#btn_search').click(function(event) {
            event.preventDefault();
            self.do_search();
            return false;
        });
        $('#tbody_task').on('change', '.update_status', function(event) {
            var task_id = $(this).closest('tr').find('td:eq(1)').find('span').attr('val');
            var task_send_type = $(this).find('input').is(':checked');
            self.update_status(task_id, task_send_type == true ? 1 : 2);
        });
        common.init_pagination($('#pagination'), function(page_index) {
            self.do_search(page_index);
        });
        $('#group, #title, #author').on('keydown', function(event) {
            if(event.keyCode == 13) {
                self.do_search();
                return false;
            }
        });
    },
    do_search: function(page_index) {
        var self = this;
        page_index = page_index || 1;
        var page_size = 25;
        var req_data = {
            'group': $('#group').val() || '',
            'title': $('#title').val() || '',
            'author': $('#author').val() || '',
            'page_index': page_index,
            'page_size': page_size,
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/rent/task_list',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    var ele_list = [];
                    for (var i = 0 ; i < res_data.data.length ; i++ ) {
                        var item = res_data.data[i];
                        var templete_task = $($('#templete_task').html().trim());
                        var name_html = [item.name];

                        if (item["ads"] && item["ads"].length > 0) {
                            var ads_html = [""];
                            for (var j = 0 ; j < item["ads"].length ; j++ ) {
                                ads_html.push('<span class="info_ads">' + item["ads"][j].replace(/&lt;/g, "<").replace(/&gt;/g, ">") + '</span>');
                            }
                            name_html.push('<br/>');
                            name_html.push(ads_html.join(" "));
                        }
                        if (item["quan"] && item["quan"].length > 0) {
                            var quan_html = [""];
                            for (var j = 0 ; j < item["quan"].length ; j++ ) {
                                quan_html.push('<span class="info_quan">' + item["quan"][j] + '</span>');
                            }
                            name_html.push('<br/>');
                            name_html.push(quan_html.join(" "));
                        }
                        if (item["promote"] && item["promote"].length > 0) {
                            var promote_html = [""];
                            for (var j = 0 ; j < item["promote"].length ; j++ ) {
                                var promote = item["promote"][j];
                                promote_html.push('<a href="' + promote[1] + '" class="info_promote">' + promote[0] + '</a>');
                            }
                            name_html.push(promote_html.join("<br/>"));
                        }

                        templete_task.find('td:eq(0)').find('a').text(item.group_name).attr("href", "https://www.douban.com/group/" + item.group + "/");
                        templete_task.find('td:eq(1)').find('a').attr('val', item.id).text(item.title).attr("href", item.href);
                        templete_task.find('td:eq(2)').find('a').attr('val', item.author_id).text(item.author).attr("href", "https://www.douban.com/people/" + item.author_id + "/");
                        templete_task.find('td:eq(3)').find('span').text(item.comment);
                        templete_task.find('td:eq(4)').find('span').text(item.date);

                        ele_list.push(templete_task);
                    }
                    common.touch_pagination(res_data.count, page_index, page_size);
                    $('#tbody_task').empty().append(ele_list);
                } else {

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
}
