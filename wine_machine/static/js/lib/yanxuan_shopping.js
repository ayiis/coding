'use strict';

window.yanxuan_shopping = {
    init: function() {
        var self = this;
        self.bind_event();
        self.do_search();
    },
    bind_event: function() {
        var self = this;
        $('#btn_search').click(function(event) {
            self.do_search();
            return false;
        });
        $('#tbody_task').on('change', '.update_status', function(event) {
            var task_id = $(this).closest('tr').find('td:eq(1)').find('span').attr('val');
            var task_send_type = $(this).find('input').is(':checked');
            self.update_status(task_id, task_send_type == true ? 1 : 2);
        });
        $('#tbody_task').on('click', '.btn-delete', function(event) {
            var tr = $(this).closest('tr')
            var task_id = tr.find('td:eq(1)').find('span').attr('val');
            self.remove_item(task_id, function(){
                tr.remove();
            });
            return false;
        });
        $('#tbody_task').on('keydown', '.good_price', function(event) {
            if(event.keyCode == 13) {
                var _id = $(this).closest('tr').attr('val');
                var good_price = $(this).val();
                good_price = Number(good_price) || 1;
                self.update_good_price(_id, good_price);
                $(this).blur();
                return false;
            }
        });
    },
    do_search: function() {
        var req_data = {
            'name': $('#name').val() || '',
            'status': Number($('#status').attr('val') || ''),
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/yanxuan/task_list',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    var ele_list = [];
                    for (var i = 0 ; i < res_data.data.length ; i++ ) {
                        var item = res_data.data[i];
                        var templete_task = $($('#templete_task').html().trim());
                        var name_html = [item["name"]];

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
                                quan_html.push('<span class="info_quan" title="' + item["quan"][j] + '">' + item["quan"][j] + '</span>');
                            }
                            name_html.push('<br/>');
                            name_html.push(quan_html.join(" "));
                        }
                        if (item["promote"] && item["promote"].length > 0) {
                            var promote_html = [""];
                            for (var j = 0 ; j < item["promote"].length ; j++ ) {
                                var promote = item["promote"][j];
                                promote_html.push('<a href="https://you.163.com/' + promote[1] + '" class="info_promote" title="' + promote[2] + '">' + promote[0] + '</a>');
                            }
                            name_html.push(promote_html.join("<br/>"));
                        }
                        templete_task.attr('val', item._id);
                        templete_task.find('td:eq(0)').find('span').attr('val', item.status || 0);
                        templete_task.find('td:eq(1)').find('span').attr('val', item._id).html(name_html.join(""));
                        templete_task.find('td:eq(2)').find('a').attr('val', item.price).text(item.price).attr("href", "https://you.163.com/item/detail?id=" + item.itemid + "");
                        templete_task.find('td:eq(3)').find('input').val(parseInt(Number(item.good_price || 0)));
                        templete_task.find('td:eq(4)').find('span').attr('val', item.stock).text(item.stock);
                        templete_task.find('td:eq(5)').find('span').attr('val', item.vender).text(item.vender);
                        templete_task.find('td:eq(6)').find('span').attr('val', item.datetime).text(item.datetime);
                        templete_task.find('.view_user_task').attr('val', item.username);

                        if(templete_task.find('td:eq(4)').find('span').attr('val') == "无货" || templete_task.find('td:eq(2)').find('a').attr('val') == "-1.00") {
                            templete_task.find('td:eq(4)').addClass("no_stock");
                        }
                        if(item.status == 1) {
                            templete_task.find('td:eq(0)').find('input').attr('checked', 'checked');
                        } else {
                            templete_task.find('td:eq(0)').find('input').attr('checked', null);
                        }
                        ele_list.push(templete_task);
                    }
                    $('#tbody_task').empty().append(ele_list);

                    if (req_data.status == 2) {
                        $('#tbody_task .btn-delete').removeClass('hide');
                    }
                } else {

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
    update_status: function(_id, status) {
        var req_data = {
            '_id': _id,
            'status': status,
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/yanxuan/task_update_status',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    $.notify("自动分发已" + (status == 1 ? "打开" : "关闭"), (status == 1 ? "success" : "info"));
                } else {
                    $.notify(res_data.desc, "warn");
                }
            },
            error: function(error) {
                $.notify(error, "error");
            }
        });
    },
    update_good_price: function(_id, good_price) {
        var req_data = {
            '_id': _id,
            'good_price': good_price,
        }
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/yanxuan/update_good_price',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    $.notify("好价已更新到" + good_price, "success");
                } else {
                    $.notify(res_data.desc, "warn");
                }
            },
            error: function(error) {
                $.notify(error, "error");
            }
        });
    },
    remove_item: function(_id, cb) {
        var req_data = {
            '_id': _id,
        }
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/yanxuan/remove_item',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    $.notify("商品已删除", "info");
                    if (cb) {
                        cb();
                    }
                } else {
                    $.notify(res_data.desc, "warn");
                }
            },
            error: function(error) {
                $.notify(error, "error");
            }
        });
    },
}
