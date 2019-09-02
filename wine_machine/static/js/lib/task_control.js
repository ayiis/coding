'use strict';

window.task_control = {
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
        });
        $('#btn_return').click(function(event) {
            event.preventDefault();
            $('#div_download').addClass('hidden');
            $('#content').removeClass('hidden');
        });
        $('#tbody_task_list').on('click', '.audit_pass', function(event) {
            var task_id = $(this).closest('tr').attr('val');
            var user_id = $(this).closest('tr').find('td:eq(2)').find('span').attr('val');
            self.update_status(task_id, 3, user_id);
            return false;
        });
        $('#tbody_task_list').on('click', '.audit_fail', function(event) {
            var task_id = $(this).closest('tr').attr('val');
            var user_id = $(this).closest('tr').find('td:eq(2)').find('span').attr('val');
            self.update_status(task_id, 1, user_id);
            return false;
        });
        $('#tbody_task_list').on('click', '.view_user_task', function(event) {
            var task_id = $(this).closest('tr').find('td:eq(1)').find('span').attr('val');
            var username = $(this).attr('val');
            window.location = '/user_task_list?task_id=' + task_id + '&username=' + username;
            return false;
        });
        $('#tbody_task_list').on('click', '.export_xls', function(event) {
            var task_raw_id = $(this).closest('tr').attr('task_id');
            var username = $(this).closest('tr').find('td:eq(2)').find('span').text();
            self.export_xls(task_raw_id, username);
        });
        $('#tbody_task_list').on('click', '.pack_wav', function(event) {
            var task_raw_id = $(this).closest('tr').attr('task_id');
            var datetime = $(this).closest('tr').find('td:eq(4)').find('span').attr('val');
            var username = $(this).closest('tr').find('td:eq(2)').find('span').text();
            var ts = parseInt(new Date(datetime).getTime() / 1000);
            self.pack_wav(task_raw_id, username, ts);
        });
    },
    do_search: function() {
        var self = this;
        var req_data = {
            'task_name': $('#task_name').val() || '',
            'task_status': Number($('#task_status').attr('val') || ''),
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/admin_control_task_list',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    var ele_list = [];
                    for (var i = 0 ; i < res_data.data.length ; i++ ) {
                        var item = res_data.data[i];
                        var templete_task_list = $($('#templete_task_list').html().trim());
                        templete_task_list.find('td:eq(0)').find('span').attr('val', item.status).text(item.status_name);
                        templete_task_list.find('td:eq(1)').find('span').attr('val', item.task_id).text(item.task_name);
                        templete_task_list.find('td:eq(2)').find('span').attr('val', item.user_id).text(item.username);
                        templete_task_list.find('td:eq(3)').find('span').attr('val', item.deadline).text(item.deadline);
                        templete_task_list.find('td:eq(4)').find('span').attr('val', item.datetime).text(item.datetime);
                        templete_task_list.find('td:eq(5)').find('span').attr('val', item.done).text( item.done + "/" + item.total);
                        templete_task_list.find('td:eq(6)').find('span').text(item.total_wav_duration);
                        templete_task_list.attr('val', item._id).attr('task_id', item.task_id);
                        if (item.status != 2) {
                            templete_task_list.find('.audit_pass').addClass('hidden');
                            templete_task_list.find('.audit_fail').addClass('hidden');
                        } else {
                            templete_task_list.find('td:eq(0)').addClass('label-warning');
                        }
                        if (self.user_role != 1) {
                            templete_task_list.find('.export_xls').addClass('hidden');
                            templete_task_list.find('.pack_wav').addClass('hidden');
                        }
                        templete_task_list.find('.view_user_task').attr('val', item.username);
                        ele_list.push(templete_task_list);
                    }
                    $('#tbody_task_list').empty().append(ele_list);
                } else {

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
    update_status: function(task_id, status, user_id){
        var req_data = {
            'task_id': task_id,
            'task_status': status,
            'user_id': user_id,
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/update_task_status',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    setTimeout(function(){
                        window.location.reload();
                    }, 200);
                } else {

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
    export_xls: function(task_id, username){
        var req_data = {
            'username': username,
            'task_id': task_id,
        };
        $('#div_wait_download').find('span').text('正在打包，请稍等..');
        self.interval = setInterval(function() {
            $('#div_wait_download').find('span').text($('#div_wait_download').find('span').text() + '.');
        }, 1000);
        $('#content').addClass('hidden');
        $('#div_wait_download').removeClass('hidden');
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/export_xls',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                window.clearInterval(self.interval);
                $('#div_download').removeClass('hidden');
                $('#div_wait_download').addClass('hidden');
                if (res_data.code == 200) {
                    $('#div_download').find('span').text('请点击下载');
                    $('#div_download').find('a').attr('href', res_data.data).text(res_data.data);
                } else {
                    $('#div_download').find('span').text('打包失败: ' + res_data.desc);
                    $('#div_download').find('a').attr('href', '##').text(null);
                }
            },
            error: function(error) {
                window.clearInterval(self.interval);
                console.log(error);
            }
        });
    },
    pack_wav: function(task_id, username, ts){
        var req_data = {
            'task_id': task_id,
            'username': username,
            'ts': ts,
        };
        $('#div_wait_download').find('span').text('正在打包，请稍等..');
        self.interval = setInterval(function() {
            $('#div_wait_download').find('span').text($('#div_wait_download').find('span').text() + '.');
        }, 1000);
        $('#content').addClass('hidden');
        $('#div_wait_download').removeClass('hidden');
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/pack_wav',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                window.clearInterval(self.interval);
                $('#div_download').removeClass('hidden');
                $('#div_wait_download').addClass('hidden');
                if (res_data.code == 200) {
                    $('#div_download').find('span').text('请点击下载');
                    $('#div_download').find('a').attr('href', res_data.data).text(res_data.data);
                } else {
                    $('#div_download').find('span').text('打包失败: ' + res_data.desc);
                    $('#div_download').find('a').attr('href', '##').text(null);
                }
            },
            error: function(error) {
                window.clearInterval(self.interval);
                console.log(error);
            }
        });
    },
}
