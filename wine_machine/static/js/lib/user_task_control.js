'use strict';

window.user_task_control = {
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
        $('#tbody_task_list').on('click', '.audit_submit', function(event) {
            var task_id = $(this).closest('tr').attr('val');
            self.update_status(task_id, 2);
        });
        $('#tbody_task_list').on('click', '.view_user_task', function(event) {
            var task_id = $(this).closest('tr').find('td:eq(1)').find('span').attr('val');
            var username = $(this).attr('val');
            window.location = '/user_task_list?task_id=' + task_id + '&username=' + username;
            return false;
        });
    },
    do_search: function() {
        var req_data = {
            'task_name': $('#task_name').val() || '',
            'task_status': Number($('#task_status').attr('val') || ''),
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/user_control_task_list',
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
                        templete_task_list.find('td:eq(2)').find('span').attr('val', item.deadline).text(item.deadline);
                        templete_task_list.find('td:eq(3)').find('span').attr('val', item.datetime).text(item.datetime);
                        templete_task_list.find('td:eq(4)').find('span').attr('val', item.done).text( item.done + "/" + item.total);
                        templete_task_list.attr('val', item._id);
                        if(item.status != 1 || item.done != item.total) {
                            templete_task_list.find('.audit_submit').addClass('hidden');
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
    update_status: function(task_id, status){

        var req_data = {
            'task_id': task_id,
            'task_status': status,
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/user_update_task_status',
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
}
