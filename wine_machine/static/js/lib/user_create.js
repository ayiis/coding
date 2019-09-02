'use strict';

window.user_create = {
    init: function() {
        var self = this;
        self.bind_event();
    },
    bind_event: function() {
        $('#btn_submit').on('click', function () {
            if (!$.trim($('#username').val()) || !$.trim($('#password').val())) {
                $('#span_message').text('用户名或密码不能为空');
                return false;
            }
            var req_data = {
                "username": $.trim($('#username').val()),
                "password": $.trim($('#password').val()),
                "user_role": Number($('#user_role').attr('val') || ''),
            };
            req_data['password'] = md5(req_data['password'], 'CQex93/zy1DkRDgHNhE9KxXTxtIlxF1h');
            $.ajax({
                url: '/api/user_create',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify(req_data),
                dataType: 'json',
                success: function (json) {
                    console.log(json);
                    if (json.code == 200) {
                        $('#span_message').text('创建成功。即将跳转到用户列表...');
                        setTimeout(function() {
                            window.location = '/user_control';
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
