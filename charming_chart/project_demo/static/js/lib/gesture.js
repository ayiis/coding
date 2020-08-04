'use strict';

window.gesture = {
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
            url: '/api/weekly_summary',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function (json) {
                console.log(json);
                if (json.code == 200) {
                    self.draw_main(echarts.init(document.getElementById("main")), json.data);
                    self.draw_main2(echarts.init(document.getElementById("main2")), json.data);
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

        var color_list = ["#c23531", "#31bec2"];
        // var color_list = ["#c23531", "#31c235", "#3531c2"];

        // 向首位取整
        var bar_height0 = parseInt(max_val / 4);
        var bar_height = self.format_int(bar_height0, ("" + bar_height0).length - 1);
        bar_height = Math.max(10, bar_height);
        var option = {
            // animation: true,
            animation: false,
            title: {
                text: '手势接口分时请求数据',
                subtext: '数据来源：gesture_api 接口',
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
                stack: '请求数量',
                silent: true,
            }, {
                type: 'bar',
                itemStyle: {
                    normal: {
                        color: function(params) {
                            if(data[params.dataIndex] <= 0) {
                                return "#cccccc";
                            }
                            return color_list[0];
                        },
                    }
                },
                data: data.map(function (d) {
                    return d;
                }),
                coordinateSystem: 'polar',
                stack: '请求数量',
                barMinHeight: 3,
                z: -2,
            }, {
                name: '最新成交价',
                stack: '请求数量',
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
                        res.push((Math.random()*10 + 5).toFixed(1) - 0);
                        len++;
                    }
                    return res;
                })(),
            }],
        };

        $my_chart.setOption(option);
    },
    draw_main2: function($my_chart, raw_data) {

        var data = [];
        var cities = [];
        for(var i=0; i < raw_data.length; i++ ) {
            // data.push([0, raw_data[i], 0]);
            data.push(raw_data[i]);
            cities.push(i);
        }

        var barHeight = 50;
        var option = {
            animation: false,
            title: {
                text: '手势接口分时请求数据',
                subtext: '数据来源：gesture_api 接口'
            },
            angleAxis: {
                type: 'category',
                data: cities,
                offset: 300,
            },
            tooltip: {
                show: true,
                formatter: function (params) {
                    var id = params.dataIndex;
                    return cities[id] + '点：' + data[id];
                }
            },
            radiusAxis: {
            },
            polar: {
            },
            series: [{
                type: 'bar',
                itemStyle: {
                    color: 'transparent'
                },
                data: data.map(function (d) {
                    return 200;
                }),
                coordinateSystem: 'polar',
                stack: '请求数量',
                silent: true
            }, {
                type: 'bar',
                data: data.map(function (d) {
                    return Math.max(d, 0);
                }),
                coordinateSystem: 'polar',
                name: '价格范围',
                stack: '请求数量',
                barMinHeight: 2,
                z: -2,
            }],
        };

        $my_chart.setOption(option);
    }
}
