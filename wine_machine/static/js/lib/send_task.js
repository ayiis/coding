'use strict';

window.send_task = {
    init: function() {
        var self = this;
        var paraObj = self.getUrlParameter();
        $('#task_id').val(paraObj['task_id']);
        $('#task_name').val(paraObj['task_name']);
        self.bind_event();
        self.init_user_list();
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
        $('#task_enable_user, #task_enable_admin').click(function() {
            if($('#task_enable_user').is(':checked')) {
                $('#select_user_list>option[role="2"]').prop('selected', true);
                $('#select_user_list').trigger('change');
            } else {
                $('#select_user_list>option[role="2"]').prop('selected', false);
                $('#select_user_list').trigger('change');
            }
            if($('#task_enable_admin').is(':checked')) {
                $('#select_user_list>option[role="1"]').prop('selected', true);
                $('#select_user_list').trigger('change');
            } else {
                $('#select_user_list>option[role="1"]').prop('selected', false);
                $('#select_user_list').trigger('change');
            }
        });
        $('#btn_submit').on('click', function() {
            var req_data = {
                "task_id": $('#task_id').val(),
                "task_name": $('#task_name').val(),
                "task_deadline": $('#task_deadline').val(),
                "task_percent": $('#task_percent').val(),
                "user_list": $('#select_user_list').val().join("|"),
            };
            $.ajax({
                url: '/api/send_task',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify(req_data),
                dataType: 'json',
                success: function (json) {
                    console.log(json);
                    if (json.code == 200) {
                        $('#span_message').text('分发成功。即将跳转到任务设置...');
                        setTimeout(function() {
                            window.location = '/task';
                        }, 2000);
                    } else {
                        $('#span_message').text('分发失败：' + json.desc);
                        $('#btn_submit').attr('disabled', null);
                    }
                },
                error: function(error) {
                    console.log(error);
                    $('#span_message').text('分发失败：' + error.status + ":" + error.statusText);
                    $('#btn_submit').attr('disabled', null);
                },
            });
            $('#btn_submit').attr('disabled', 'disabled');
            $('#span_message').text('请稍等...');
            return false;
        });
    },
    init_user_list: function() {
        var req_data = {
            "task_id": $('#task_id').val(),
            "status": 1,
        };
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
                        ele_list.push('<option value="' + item._id + '" role="' + item.role + '">' + item.username + '@' + item.role_name + '</option>');
                    }
                    $('#select_user_list').empty().append(ele_list);
                    $('#select_user_list').select2();
                } else {
                    $('.select2-selection__rendered').text('Error: 未查询到任何用户，请刷新后再试')
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    }
}
