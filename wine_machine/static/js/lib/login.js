'use strict';

(function() {
    $('#btn_submit').click(function(event) {
        event.preventDefault();
        var req_data = {
            'username': $('#username').val(),
            'password': $('#password').val(),
            'ts': (new Date).getTime(),
        }
        req_data['password'] = md5(req_data['password'], 'CQex93/zy1DkRDgHNhE9KxXTxtIlxF1h');
        if(req_data.username && req_data.password) {
            $.ajax({
                type: 'POST',
                contentType: 'application/json; charset=UTF-8',
                url: '/api/login',
                data: JSON.stringify(req_data),
                dataType: 'json',
                success: function(res_data) {
                    if (res_data.code === 200) {
                        window.location = '/user_task_control';
                    } else {
                        $('#password').val(null);
                        $('#error_message').text(res_data.desc);
                    }
                },
                error: function(error) {
                    $('#password').val(null);
                    $('#error_message').text(error.responseText);
                }
            });
        } else {
            $('#error_message').text('Input an username and a password.');
        }
    });
})();
