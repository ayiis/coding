(function() {
    window.mine = {
        init: function() {
            var self = this;
            console.log(1);
            $('#btn_start').on('click', function() {
                console.log(2);
                self.get_start();
                return false;
            });
        },
        djb2: function(str) {
            var hash = 5381;
            for (var i = 0; i < str.length; i++) {
                hash = ((hash << 5) + hash) + str.charCodeAt(i); /* hash * 33 + c */
            }
            return hash;
        },
        hashStringToColor: function (str) {
            var hash = md5(str);
            var rgb = '#' + hash.substring(0, 6);
            return rgb;
            // var hash = this.djb2(str);
            // var r = (hash & 0xFF0000) >> 16;
            // var g = (hash & 0x00FF00) >> 8;
            // var b = hash & 0x0000FF;
            // return "#" + ("0" + r.toString(16)).substr(-2) + ("0" + g.toString(16)).substr(-2) + ("0" + b.toString(16)).substr(-2);
        },
        get_start: function() {
            var self = this;
            $.ajax({
                url: '/get_start',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify({'url': $('#url').val()}),
                dataType: 'json',
                success: function (json) {
                    if (json.code == 200 && json.data) {
                        $('#raw_title').text(json.data.title);
                        $('#raw_text').text(json.data.article);
                        self.get_cut_and_recognize(json.data.article);
                    }
                    else {
                        $('#raw_text').text("解析失败" + str(json.desc));
                    }
                },
                error: function(error) {
                    $('#raw_text').text("解析失败" + str(error));
                },
            });
        },
        get_cut_and_recognize: function(text) {
            var self = this;
            $.ajax({
                url: '/get_cut_and_recognize',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify({'text': text}),
                dataType: 'json',
                success: function (json) {
                    if (json.code == 200 && json.data) {
                        $('#text_cut').html(json.data.cut + "<br><br><br>使用词典：《通用词典》");
                        var recognize = json.data.recognize;
                        var temp_text = "";
                        var last_point = 0;
                        var syntax_list = {};
                        for (var i = 0 ; i < recognize.length ; i++) {
                            var sep = recognize[i];
                            temp_text += text.substring(last_point - 1, sep[0]);
                            last_point = sep[1];
                            // var innertext = text.substr(sep[0], sep[1]);
                            syntax_list[sep[2]] = syntax_list[sep[2]] || self.hashStringToColor(sep[2]);
                            temp_text += '<span style="color:' + syntax_list[sep[2]] + '">' + sep[3] + '</span>';
                        }
                        temp_text += text.substring(last_point);
                        temp_text += '<br><br><br>使用词典：《通用词典》<br>染色：';
                        for(var key in syntax_list) {
                            temp_text += ' <span style="color:' + syntax_list[key] + '">' + key + '</span> ';
                        }
                        $('#text_recognize').html(temp_text);
                    }
                    else {
                        $('#text_cut,#text_recognize').text("解析失败" + str(json.desc));
                    }
                },
                error: function(error) {
                    $('#text_cut,#text_recognize').text("解析失败" + str(error));
                },
            });
        },
    };
    window.mine.init();
})();
