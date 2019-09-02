'use strict';

window.user_control = {
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
        $('#tbody_user_list').on('change', '.update_user_status', function(event) {
            var new_status = $(this).find('input').is(':checked');
            var user_id = $(this).closest('tr').attr('val');
            self.user_status_update(user_id, new_status == true ? 1 : -1); // change to another status
        });
        $('#tbody_user_list').on('click', '.user_set', function(event) {
            var user_id = $(this).closest('tr').attr('val');
            var user_role = $(this).closest('tr').find('td:eq(1)').find('span').attr('val');
            var username = $(this).closest('tr').find('td:eq(2)').find('span').text();
            window.location = '/user_set?user_id=' + user_id + '&user_role=' + user_role + '&username=' + username;
            return false;
        });
    },
    do_search: function() {
        var req_data = {
            'username': $('#username').val() || '',
            'user_role': Number($('#user_role').attr('val') || ''),
            'return_task': true,
        }
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/user_list',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    var ele_list = [];
                    for (var i = 0 ; i < res_data.data.length ; i++ ) {
                        var item = res_data.data[i];
                        var templete_user_list = $($('#templete_user_list').html().trim());
                        templete_user_list.find('td:eq(0)').find('span').attr('val', item.status).text();
                        templete_user_list.find('td:eq(1)').find('span').attr('val', item.role).text(item.role_name);
                        templete_user_list.find('td:eq(2)').find('span').attr('val', item._id).text(item.username);
                        if (!!item.all_task) {
                            var all_task_list = [];
                            var done_task_list = [];
                            for (var j = 0 ; j < item.all_task.length ; j++ ) {
                                var task = item.all_task[j];
                                var a_ele = '<a href="user_task_list?task_id=' + task.task_id + '&username=' + item.username + '">' + task.task_name + '</a>';
                                all_task_list.push(a_ele);
                                if (task.status == 3) {
                                    done_task_list.push(a_ele);
                                }
                            }
                            templete_user_list.find('td:eq(3)').find('span').html(all_task_list.join("<br>"));
                            templete_user_list.find('td:eq(4)').find('span').html(done_task_list.join("<br>"));
                            templete_user_list.find('td:eq(5)').find('span').text(done_task_list.length + '/' + all_task_list.length);
                        }
                        templete_user_list.find('td:eq(6)').find('span').attr('val', item.datetime).text(item.datetime);
                        templete_user_list.attr('val', item._id);
                        if(item.role == 1) {
                            templete_user_list.find('td:eq(1)').addClass('label-info');
                        } else {
                        }
                        if(item.status == 1) {
                            templete_user_list.find('td:eq(0)').find('input').attr('checked', 'checked');
                        } else {
                            templete_user_list.find('td:eq(0)').find('input').attr('checked', null);
                        }
                        ele_list.push(templete_user_list);
                    }
                    $('#tbody_user_list').empty().append(ele_list);
                } else {

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
    user_status_update: function(user_id, status) {

        var req_data = {
            'user_id': user_id,
            'status': status
        }
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/user_status_update',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    // setTimeout(function() {
                    //     window.location.reload();
                    // }, 200);
                } else {

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
}
