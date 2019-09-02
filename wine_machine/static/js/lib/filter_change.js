'use strict';

window.filter_change = {
    init: function() {
        var self = this;
        self.bind_event();
        self.do_search();
    },
    bind_event: function() {
        var self = this;
        $('#btn_search').click(function(event) {
            event.preventDefault();
            self.do_search();
            return false;
        });
        $('#btn_submit').on('click', function(event) {
            self.change_filter();
        });
        $('#btn_rtn').on('click', function(event) {
            return window.history.go(-1);
        });
    },
    do_search: function() {
        var req_data = {
            "website": "douban",
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/rent/query_filter',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    $("#title").val(res_data.data["title"].join("'"));
                    $("#author").val(res_data.data["author"].join("'"));
                    $("#author_full_name").val(res_data.data["author_full_name"].join("'"));
                    $("#not").val(res_data.data["not"].join("'"));
                    $("#price_min").val(res_data.data["price_min"]);
                    $("#price_max").val(res_data.data["price_max"]);
                } else {

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    },
    change_filter: function(_id, status) {
        var req_data = {
            "website": "douban",
            "title": $("#title").val().split("'"),
            "author": $("#author").val().split("'"),
            "author_full_name": $("#author_full_name").val().split("'"),
            "price_min": Number($("#price_min").val()),
            "price_max": Number($("#price_max").val()),
            "not": $("#not").val().split("'"),
        };
        $("#btn_submit").attr("disabled", "disabled");
        $("#span_message").text("...");
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/api/rent/change_filter',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                if (res_data.code == 200) {
                    $("#span_message").text("修改成功");
                } else {

                }
                $("#btn_submit").attr("disabled", null);
            },
            error: function(error) {
                console.log(error);
                $("#btn_submit").attr("disabled", null);
            }
        });
    },
}
