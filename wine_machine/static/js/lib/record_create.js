'use strict';

window.record_create = {
    init: function() {
        var self = this;

        // self.history = -1;
        self.recorder = Recorder();
        self.audio = $('#audio')[0];
        self.blob = null;

        self.recorder.open(function() {
            $('#span_message').text('点击开始录音');
        },function(msg) {
            $('#span_message').text('无法录音:' + msg);
        });

        var paraObj = self.getUrlParameter(location.hash.replace(/^#*/g, ''));
        self._id = paraObj['_id'];
        self.task_id = paraObj['task_id'];
        self.bind_event();
        self.record_get_next(0);
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
        var self = this;
        $('#btn_start').on('click', function() {
            self.recorder.start();
            $('#btn_stop').attr('disabled', null);
            $('#btn_start,#btn_submit,#btn_prev,#btn_next').attr('disabled', 'disabled');
            $('#btn_start').addClass('btn-rotate');
            return false;
        });
        $('#btn_stop').on('click', function() {
            $('#btn_stop').attr('disabled', 'disabled');
            self.recorder.stop(function(blob, duration){
                self.blob = blob;
                // self.recorder.close();
                $('#span_message').text('时长:' + duration + 'ms');
                $('#btn_start,#btn_submit,#btn_prev,#btn_next').attr('disabled', null);
                $('#btn_start').removeClass('btn-rotate');
            },function(msg){
                self.blob = null;
                $('#span_message').text('录音失败:' + msg);
            });
            return false;
        });
        $('#btn_play').on('click', function() {
            if(self.blob) {
                self.audio.src = window.URL.createObjectURL(self.blob);
                self.audio.play();
            } else if (self.audio.src) {
                self.audio.play();
            }
            return false;
        });
        $('#btn_submit').on('click', function() {
            if (!self.blob) {
                return false;
            }
            var formData = new FormData();
            formData.append('_id', self._id);
            formData.append('task_id', self.task_id);
            formData.append('audioData', self.blob);
            $.ajax({
                url: '/api/record_upload',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                dataType: 'json',
                success: function (json) {
                    console.log(json);
                    if (json.code == 200) {
                        $('#download_wav').removeClass('hidden');
                        $('#download_wav').attr('href', json.data.voice_path);
                    }
                    $('#span_message').text(json.desc);
                    $('#btn_submit').attr('disabled', null);
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


        $('#btn_prev').on('click', function() {
            self.record_get_next(-1);
            return false;
        });
        $('#btn_next').on('click', function() {
            self.record_get_next(1);
            return false;
        });
    },
    record_get_next: function(next) {
        var self = this;
        var req_data = {
            "_id": self._id,
            "task_id": self.task_id,
            "next": next,
        };
        $.ajax({
            url: '/api/record_get_next',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function (json) {
                console.log(json);
                if (json.code == 200) {
                    $('#record_text').text(json.data.text);
                    window.location.hash = '##_id=' + json.data._id + '&task_id=' + json.data.task_id;
                    self._id = json.data._id;
                    self.task_id = json.data.task_id;
                    $('#audio').attr('src', json.data.voice_path + '?ts=' + new Date().getTime());
                    self.blob = null;
                    if (json.data.voice_path) {
                        $('#download_wav').attr('href', json.data.voice_path + '?ts=' + new Date().getTime());
                        $('#download_wav').removeClass('hidden');
                    } else {
                        $('#download_wav').attr('href', null);
                        $('#download_wav').addClass('hidden');
                    }
                    $('#span_message').text('');
                } else {
                    $('#span_message').text('查询失败：' + json.desc);
                    $('#btn_submit').attr('disabled', null);
                }
            },
            error: function(error) {
                console.log(error);
                $('#span_message').text('已经到底了');
                $('#btn_submit').attr('disabled', null);
            },
        });
    }
}
