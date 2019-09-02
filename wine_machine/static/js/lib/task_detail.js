'use strict';

window.task_detail = {
    init: function() {
        var self = this;
        self.bind_event();
        self.init_data();
    },
    bind_event: function() {
        var self = this;
        $('#btn_return').click(function(event) {
            window.history.back(-1);
            return false;
        });
    },
    getUrlParameter: function(url) {
        url = url || location.href;
        var paraString = url.substring(url.indexOf('?') + 1, url.length).split('&');
        var paraObj = {};
        paraString.forEach(function(e){
            paraObj[decodeURIComponent(e.split('=')[0])] = decodeURIComponent(e.split('=')[1]);
        });
        return paraObj;
    },
    init_data: function() {
        var self = this;
        var paraObj = self.getUrlParameter();
        var req_data = {
            'task_id': paraObj.task_id,
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/task_detail',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    var ele_list = [];
                    var task_detail = res_data.data;
                    $('#task_name').text(task_detail['task_name']);
                    $('#datetime').text(task_detail['datetime']);
                    $('#task_deadline').text(task_detail['task_deadline']);
                    $('#file_name').text(task_detail['file_name']);
                    $('#file_path').attr('href', "/" + task_detail['file_path']).text(task_detail['file_path']);
                    $('#file_content').val(task_detail['file_content']);
                } else {
                    console.log(error);
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
}
