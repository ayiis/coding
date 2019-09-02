'use strict';

window.user_task_list = {
    init: function() {
        var self = this;
        var href_query = self.getUrlParameter();
        if(href_query.task_id && href_query.username) {
            self.task_id = href_query.task_id;
            self.username = href_query.username;
        }
        self.bind_event();
        self.do_search();
    },
    getUrlParameter: function(url) {
        url = url || location.href;
        var paraString = url.substring(url.indexOf('?') + 1, url.length).split('&');
        var paraObj = {};
        paraString.forEach(function(e) {
            paraObj[decodeURIComponent(e.split('=')[0])] = decodeURIComponent(e.split('=')[1]);
        });
        return paraObj;
    },
    bind_event: function() {
        var self = this;
        $('#btn_search').click(function(event) {
            event.preventDefault();
            self.do_search();
        });
        // $('#tbody_user_task_list').on('click', '.dubbing_create, .dubbing_change', function(event) {
        //     var user_task_id = $(this).closest('tr').attr('val');
        //     var task_id = $(this).closest('tr').find('td:eq(1)').find('span').attr('val');
        //     var href = '/record_create##_id=' + user_task_id + '&task_id=' + task_id;
        //     window.location = href;
        //     return false;
        // });
        $('#tbody_user_task_list').on('click', '.play_record', function(event) {
            var record_url = $(this).closest('tr').attr('voice_path');
            $('#audio').attr('src', record_url + '?ts=' + new Date().getTime());
            $('#audio')[0].play();
            return false;
        });
        $('#tbody_user_task_list').on('click', '.audit_pass', function(event) {
            var task_id = $(this).closest('tr').attr('val');
            self.update_audit_status(task_id, 1);
            return false;
        });
        $('#tbody_user_task_list').on('click', '.audit_fail', function(event) {
            var task_id = $(this).closest('tr').attr('val');
            self.update_audit_status(task_id, 2);
            return false;
        });
    },
    do_search: function() {
        var self = this;
        var req_data = {
            'task_name': $('#task_name').val() || '',
            'task_status': Number($('#task_status').attr('val') || ''),
        };
        if(self.task_id) {
            req_data['task_id'] = self.task_id;
            req_data['username'] = self.username;
        }
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/user_task_list',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    var ele_list = [];
                    for (var i = 0 ; i < res_data.data.length ; i++ ) {
                        var item = res_data.data[i];
                        var templete_user_task_list = $($('#templete_user_task_list').html().trim());
                        templete_user_task_list.find('td:eq(0)').find('span').attr('val', item.status).text(item.status_name);
                        templete_user_task_list.find('td:eq(1)').find('span').attr('val', item.task_id).text(item.task_name);
                        templete_user_task_list.find('td:eq(2)').find('span').attr('val', item.user_id).text(item.username);
                        templete_user_task_list.find('td:eq(3)').find('span').attr('val', item.text).text(item.text);
                        templete_user_task_list.find('td:eq(4)').find('span').attr('val', item.datetime).text(item.datetime);
                        templete_user_task_list.attr('val', item._id).attr('voice_path', item.voice_path);
                        if(item.status == 2) {
                            templete_user_task_list.find('.dubbing_create').addClass('hidden');
                        } else {
                            templete_user_task_list.find('.dubbing_change').addClass('hidden');
                            templete_user_task_list.find('.play_record').addClass('hidden');
                        }
                        templete_user_task_list.find('.dubbing_create, .dubbing_change').attr(
                            'href', '/record_create##_id=' + item._id + '&task_id=' + item.task_id
                        );
                        if(self.real_username != item.username) {
                            templete_user_task_list.find('.dubbing_create,.dubbing_change').addClass('hidden');
                        }
                        if(self.user_role == 1) {
                            if (item.audit_status == 1) {
                                templete_user_task_list.find('>td:eq(0)').addClass('label-success');
                            }
                        } else {
                            templete_user_task_list.find('.audit_pass, .audit_fail').addClass('hidden');
                        }
                        if(item.audit_status == 2) {
                            templete_user_task_list.find('>td:eq(0)').addClass('label-warning');
                        }

                        ele_list.push(templete_user_task_list);
                    }
                    $('#tbody_user_task_list').empty().append(ele_list);
                } else {

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
    update_audit_status: function(task_id, audit_status){
        var req_data = {
            'task_id': task_id,
            'audit_status': audit_status,
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/update_user_task_audit_status',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    // setTimeout(function() {
                    //     window.location.reload();
                    // }, 2000);
                    if(audit_status == 1) {
                        $('#tbody_user_task_list').find('>tr[val=' + task_id + ']').find('>td:eq(0)').removeClass('label-warning').addClass('label-success');
                    } else {
                        $('#tbody_user_task_list').find('>tr[val=' + task_id + ']').find('>td:eq(0)').removeClass('label-success').addClass('label-warning');
                    }
                    var total = $('#tbody_user_task_list').find('>tr').length;
                    var fail_count = $('#tbody_user_task_list').find('.label-warning').length;
                    var success_count = $('#tbody_user_task_list').find('.label-success').length;
                    $.notify('总数：' + total + '； 退回/通过： ' + fail_count + '/' + success_count, 'success');
                } else {
                    $.notify(res_data.desc, 'warn');
                }
            },
            error: function(error) {
                $.notify(error, 'error');
                console.log(error);
            }
        });
    },
}
