'use strict';

(function() {
    $('#btn_submit').click(function(event) {

        if (!$.trim($('#username').val()) || !$.trim($('#password').val())) {
            $('#error_message').text('用户名或密码不能为空');
            return false;
        }
        if($('#password').val() != $('#confirm_password').val()){
            $('#error_message').text('两次密码不一致');
            return false;
        }
        var req_data = {
            'username': $('#username').val(),
            'password': $('#password').val(),
            'ts': (new Date).getTime(),
        }
        if (!/^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$/.test(req_data['username'])){
            $('#error_message').text('用户名需以邮箱注册，请检查邮箱格式');
            return false;
        }
        req_data['password'] = md5(req_data['password'], 'CQex93/zy1DkRDgHNhE9KxXTxtIlxF1h');
        if(req_data.username && req_data.password) {
            $.ajax({
                type: 'POST',
                contentType: 'application/json; charset=UTF-8',
                url: '/api/user_signup' + window.location.search,
                data: JSON.stringify(req_data),
                dataType: 'json',
                success: function(res_data) {
                    if (res_data.code === 200) {
                        $('#error_message').text('注册成功，即将跳转到登录页面');
                        setTimeout(function() {
                            window.location = '/login';
                        }, 2000);

                    } else {
                        $('#error_message').text(res_data.desc);
                    }
                },
                error: function(error) {
                    $('#error_message').text(error.responseText);
                }
            });
        } else {
            $('#error_message').text('Input username and password.');
        }

        return false;
    });
})();
