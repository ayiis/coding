'use strict';

window.task_create = {
    init: function() {
        var self = this;
        self.bind_event();
        self.init_user_list();
    },
    bind_event: function() {
        $('#select_task').on('click', function() {
            $('#task_file').click();
        });
        $('#task_file').on('change', function() {
            if (this.files.length == 0) {
                $(this).parent().find('.avatar-file-name').text('未选择文件');
            } else {
                $(this).parent().find('.avatar-file-name').text('已选择 ' + this.files[0].name + ', ' + (this.files[0].size/1024).toFixed(2) + 'kb');
            }
        });
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
            var formData = new FormData();
            formData.append('task_file', $('#task_file')[0].files[0]);
            formData.append('task_name', $('#task_name').val());
            formData.append('task_deadline', $('#task_deadline').val());
            formData.append('task_percent', $('#task_percent').val());
            formData.append('user_list', $('#select_user_list').val().join("|"));
            $.ajax({
                url: '/api/task_create',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                dataType: 'json',
                success: function (json) {
                    console.log(json);
                    if (json.code == 200) {
                        $('#span_message').text('创建成功。即将跳转到任务列表...');
                        setTimeout(function() {
                            window.location = '/task_control';
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
    },
    init_user_list: function() {
        var req_data = {
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
