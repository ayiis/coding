'use strict';

(function() {
    $('#btn_submit').click(function(event) {
        event.preventDefault();
        if(!$('#new_password').val() || !$('#password').val()) {
            $('#span_message').text('请输入密码');
            return false;
        }
        if($('#new_password').val() == $('#password').val()) {
            $('#span_message').text('新旧密码相同');
            return false;
        }
        if($('#new_password').val() != $('#new_password_confirm').val()){
            $('#span_message').text('两次新密码不一致');
            return false;
        }
        var req_data = {
            'password': $('#password').val(),
            'new_password': $('#new_password').val(),
        }
        req_data['password'] = md5(req_data['password'], 'CQex93/zy1DkRDgHNhE9KxXTxtIlxF1h');
        req_data['new_password'] = md5(req_data['new_password'], 'CQex93/zy1DkRDgHNhE9KxXTxtIlxF1h');
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=UTF-8',
            url: '/api/change_password',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code === 200) {
                    $('#span_message').text('你的新密码已生效，请重新登录');
                    setTimeout(function(){
                        window.location = '/login';
                    }, 2000);
                } else {
                    $('#password').val(null);
                    $('#span_message').text(res_data.desc);
                }
            },
            error: function(error) {
                $('#password').val(null);
                $('#span_message').text(error.responseText);
            }
        });

        return false;
    });
})();
