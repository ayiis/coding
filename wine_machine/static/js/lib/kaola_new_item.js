'use strict';

window.kaola_new_item = {
    init: function() {
        var self = this;
        self.bind_event();
    },
    bind_event: function() {
        $('#btn_submit').on('click', function() {
            if (!$('#itemid_list').val()) {
                $('#span_message').text('请输入名称');
                return false;
            }
            var req_data = {
                "status": $('#status').find('input').is(':checked') ? 1 : 2,
                "itemid_list": $('#itemid_list').val().split(","),
            }
            $.ajax({
                url: '/api/kaola/task_add',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify(req_data),
                dataType: 'json',
                success: function (json) {
                    console.log(json);
                    if (json.code == 200) {
                        $('#span_message').text('创建成功。即将跳转到任务设置...');
                        setTimeout(function() {
                            window.location = '/kaola_shopping';
                        }, 2000);
                    } else {
                        $('#span_message').text('创建失败：' + json.desc);
                        $('#btn_submit').attr('disabled', null);
                    }
                },
                error: function(error) {
                    console.log(error);
                    $('#span_message').text('创建失败：' + error.status + ":" + error.statusText);
                    $('#btn_submit').attr('disabled', null);
                },
            });
            $('#btn_submit').attr('disabled', 'disabled');
            $('#span_message').text('请稍等...');
            return false;
        });
    }
}
