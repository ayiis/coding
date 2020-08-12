'use strict';

window.gesture = {
    github_color: ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
    init: function() {
        var self = this;
        self.bind_event();
        self.load_daily_data();
    },
    bind_event: function() {

    },
    load_daily_data: function() {
        var self = this;
        var req_data = {
            // "status": $('#status').find('input').is(':checked') ? 1 : 2,
            // "itemid_list": $('#itemid_list').val().split(",")
        }
        $.ajax({
            url: '/api/daily_summary',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function (json) {
                console.log(json);
                if (json.code == 200) {
                    self.draw_main(echarts.init(document.getElementById("main")), json.data["daily"]);
                    self.draw_main2(echarts.init(document.getElementById("main2")), json.data["weekly"]);
                } else {
                    ;
                }
            },
            error: function(error) {
                console.log(error);
            },
        });
        return false;
    },
    format_int: function(num, prec = 2, ceil = true) {
        var len = ("" + num).length;
        if (len <= prec) { 
            return num;
        }; 
        var mult = Math.pow(10, prec);
        return ceil ? Math.ceil(num / mult) * mult : Math.floor(num / mult) * mult;
    },
    draw_main: function($my_chart, raw_data) {
        var self = this;
        var data = [];
        var cities = [];
        var max_val = 0;
        for(var i=0; i < raw_data.length; i++ ) {
            data.push(raw_data[i]);
            cities.push(i);
            max_val = Math.max(max_val, raw_data[i]);
        }

        var color_list = ["#9be9a8", "#e99bdc"];
        // var color_list = ["#d48265", "#65d482", "#8265d4"];
        // var color_list = ["#c23531", "#31c235", "#3531c2"];

        // 向首位取整
        var bar_height0 = parseInt(max_val / 4);
        var bar_height = self.format_int(bar_height0, ("" + bar_height0).length - 1);
        bar_height = Math.max(10, bar_height);
        var option = {
            // animation: true,
            animation: false,
            title: {
                text: 'commit daily',
                // subtext: 'Github: iceyang',
                // subtext: 'Github: ayiis',
            },
            angleAxis: {
                type: 'category',
                data: cities,
                scale: true,
                axisTick: {
                    show: true,
                },
                axisLabel: {
                    show: true,
                },
            },
            tooltip: {
                show: true,
                formatter: function (params) {
                    var id = params.dataIndex;
                    return cities[id] + '点：' + data[id];
                },
            },
            radiusAxis: {
                axisLine: {
                    show: true,
                },
                axisTick: {
                    show: true,
                },
                axisLabel: {
                    formatter: function(value, index) {
                        if(value < bar_height) {
                            return null;
                        }
                        return value - bar_height;
                    },
                },
                // min: 0,
                // splitNumber: 5,
                interval: bar_height,
                // min: -bar_height,
            },
            polar: {
            },
            series: [{
                type: 'bar',
                itemStyle: {
                    color: 'transparent',
                },
                data: data.map(function (d) {
                    return bar_height;
                }),
                coordinateSystem: 'polar',
                stack: 'testcount',
                silent: true,
            }, {
                type: 'bar',
                itemStyle: {
                    normal: {
                        color: function(params) {
                            if(data[params.dataIndex] <= 0) {
                                return self.github_color[0];
                            }
                            var sel = Math.min(4, Math.max(Math.round(params.data / (max_val / 4)), 1));
                            console.log(sel);
                            return self.github_color[sel];
                        },
                    }
                },
                data: data.map(function (d) {
                    return d;
                }),
                coordinateSystem: 'polar',
                stack: 'testcount',
                barMinHeight: 3,
                z: -2,
            }, {
                name: 'testname',
                stack: 'testcount',
                type: 'line',
                smooth: true,
                itemStyle: {
                },
                color: color_list[1],
                coordinateSystem: 'polar',
                data: (function () {
                    var res = [];
                    var len = 0;
                    while (len < 24) {
                        // res.push((Math.random()*10 + 5).toFixed(1) - 0);
                        res.push(0);
                        len++;
                    }
                    return res;
                })(),
            }],
        };

        $my_chart.setOption(option);
    },
    draw_main2: function($my_chart, raw_data) {

        var self = this;
        var data = [];
        var cities = [];
        // var weekmap = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
        var weekmap = ["Sun.", "Mon.", "Tues.", "Wed.", "Thur.", "Fri.", "Sat."];
        var max_val = 0;
        for(var i=0; i < raw_data.length; i++ ) {
            data.push(raw_data[i]);
            cities.push(weekmap[i]);
            max_val = Math.max(max_val, raw_data[i]);
        }

        var color_list = ["#49ecd6", "#ec495f"];
        // var color_list = ["#d48265", "#65d482", "#8265d4"];
        // var color_list = ["#c23531", "#31c235", "#3531c2"];

        // 向首位取整
        var bar_height0 = parseInt(max_val / 4);
        var bar_height = self.format_int(bar_height0, ("" + bar_height0).length - 1);
        bar_height = Math.max(10, bar_height);
        var option = {
            // animation: true,
            animation: false,
            title: {
                text: 'commit weekly',
                // subtext: 'Github: iceyang',
                // subtext: 'Github: ayiis',
            },
            angleAxis: {
                type: 'category',
                data: cities,
                scale: true,
                axisTick: {
                    show: true,
                },
                axisLabel: {
                    show: true,
                },
            },
            tooltip: {
                show: true,
                formatter: function (params) {
                    var id = params.dataIndex;
                    return weekmap[id] + "：" + data[id];
                },
            },
            radiusAxis: {
                axisLine: {
                    show: true,
                },
                axisTick: {
                    show: true,
                },
                axisLabel: {
                    formatter: function(value, index) {
                        if(value < bar_height) {
                            return null;
                        }
                        return value - bar_height;
                    },
                },
                // min: 0,
                // splitNumber: 5,
                interval: bar_height,
                // min: -bar_height,
            },
            polar: {
            },
            series: [{
                type: 'bar',
                itemStyle: {
                    color: 'transparent',
                },
                data: data.map(function (d) {
                    return bar_height;
                }),
                coordinateSystem: 'polar',
                stack: 'testcount',
                silent: true,
            }, {
                type: 'bar',
                itemStyle: {
                    normal: {
                        color: function(params) {
                            if(data[params.dataIndex] <= 0) {
                                return self.github_color[0];
                            }
                            var sel = Math.min(4, Math.max(Math.round(params.data / (max_val / 4)), 1));
                            console.log(sel);
                            return self.github_color[sel];
                        },
                    }
                },
                data: data.map(function (d) {
                    return d;
                }),
                coordinateSystem: 'polar',
                stack: 'testcount',
                barMinHeight: 3,
                z: -2,
            }, {
                name: 'testname',
                stack: 'testcount',
                type: 'line',
                smooth: true,
                itemStyle: {
                },
                color: color_list[1],
                coordinateSystem: 'polar',
                data: (function () {
                    var res = [];
                    var len = 0;
                    while (len < 7) {
                        // res.push((Math.random()*10 + 5).toFixed(1) - 0);
                        res.push(0);
                        len++;
                    }
                    return res;
                })(),
            }],
        };

        $my_chart.setOption(option);
    }
}
