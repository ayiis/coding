'use strict';

window.user_set = {
    init: function() {
        var self = this;
        var paraObj = self.getUrlParameter();
        $('#username').val(paraObj["username"]);
        $('#user_id').val(paraObj["user_id"]);
        $('#user_role').attr('val', paraObj["user_role"]);
        $('#user_role').text($('.dropdown-menu').find('li>a[val=' + paraObj["user_role"] + ']').text());
        self.bind_event();
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
    bind_event: function() {
        $('#btn_submit').on('click', function () {
            var req_data = {
                "username": $.trim($('#username').val()),
                "user_id": $.trim($('#user_id').val()),
                "password": $.trim($('#password').val()),
                "user_role": Number($('#user_role').attr('val') || ''),
            };
            if (req_data['password']) {
                req_data['password'] = md5(req_data['password'], 'CQex93/zy1DkRDgHNhE9KxXTxtIlxF1h');
            }
            $.ajax({
                url: '/api/user_set',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify(req_data),
                dataType: 'json',
                success: function (json) {
                    console.log(json);
                    if (json.code == 200) {
                        $('#span_message').text('设置成功。即将跳转到用户列表...');
                        setTimeout(function() {
                            window.location = '/user_control';
                        }, 2000);
                    } else {
                        $('#span_message').text('设置失败：' + json.desc);
                        $('#btn_submit').attr('disabled', null);
                    }
                },
                error: function(error) {
                    console.log(error);
                    $('#span_message').text('设置失败：' + error.status + ":" + error.statusText);
                    $('#btn_submit').attr('disabled', null);
                },
            });
            $('#btn_submit').attr('disabled', 'disabled');
            $('#span_message').text('请稍等...');
            return false;
        });
    }
}
