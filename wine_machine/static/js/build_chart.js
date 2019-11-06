// https://www.echartsjs.com/zh/option.html#series-candlestick
!(function(){

window.build_good_chart = function(settings) {
    var downColor = '#5b5';  // e00
    var downBorderColor = '#5b5'; // 900
    var upColor = '#d55';   // ef3
    var upBorderColor = '#d55';  // aa3

    var option = {
        tooltip: {
            trigger: 'item',
            formatter: callback_tooltip,
            axisPointer: {
                type: 'cross'
            }
        },
        grid: {
            bottom: 30,
            top: 20,
            left: 60,
            right: 60,
        },
        animation: false,
        xAxis: {
            scale: true,
            data: settings.x,
            splitLine: {
                show: false,
            },
        },
        yAxis: {
            // scale: true,
            min: settings.x_start,
            splitArea: {
                show: true
            },
            splitLine: {
                show: false,
            },
        },
        dataZoom: [{type: 'inside'}],
        series: [
            {
                // name: 'none',
                type: 'candlestick',
                data: settings.y,
                itemStyle: {
                    normal: {
                        color: upColor,
                        color0: downColor,
                        borderColor: upBorderColor,
                        borderColor0: downBorderColor,
                        borderWidth: 2,
                    }
                },
                markLine: {
                    symbol: "none",
                    data: [{
                        yAxis: settings.good,
                        name: '好价',
                        lineStyle: {
                            normal: {
                                color: "#b27",
                                width: 2,
                                type: "dashed",
                            }
                        }
                    }, ],
                },
            }, {
                name: '低价',
                type: 'line',
                data: calculate_min(),
                smooth: true,
                lineStyle: {
                    normal: {
                        color: "#e95",
                        opacity: 0.5,
                        type: "dashed",
                    }
                }
            },
        ],
    }

    function calculate_min() {
        var result = [];
        for (var i = 0, len = settings.y.length; i < len; i++) {
            result.push(settings.y[i][2]);
        }
        return result;
    }

    function callback_tooltip(params) {
        if(params.componentType === "series") {
            if (params.seriesType === "line") {
                // return params.seriesName + ": " + params.value;
                return "原价: " + settings.prices[params['dataIndex']] + "; 低价: " + params.value + '<br>' + settings.tips[params['dataIndex']];
            }
            var last_index = params['dataIndex'] - 1;
            var chajia = 0;
            if (last_index >= 0) {
                chajia = (params.data[3] - settings.y[last_index][2]).toFixed(2);
            }
            var text = ["最低价: " + params.data[3] + (chajia>=0?'<i style="color:'+upColor+'"> +':'<i style="color:'+downColor+'"> ') + chajia + '</i>'];
            text.push("最高价: " + params.data[4]);
            text.push("开: " + params.data[1]);
            text.push("收: " + params.data[2]);
            return text.join('<br>');
        } else if (params.componentType === "markLine") {
            return params.name + ": " + params.value;
        }
        return params.name + ": " + params.value;
    }

    var eleid = settings.ele.getAttribute('id');
    if(!window.build_good_chart[eleid]) {
        window.build_good_chart[eleid] = echarts.init(settings.ele);
    }
    var chart = window.build_good_chart[eleid];
    chart.clear();
    chart.setOption(option);

}

if(false) {

    var settings = {
        "ele": $('#ffff')[0],
        "tips": [],
        // x轴
        "x": ["2019-08-01", "2019-08-03", "2019-08-04", "2019-08-05", "2019-08-07", "2019-08-08", "2019-08-09", "2019-08-14", "2019-08-15", "2019-08-16", "2019-08-21", "2019-08-27", "2019-08-28", "2019-08-29", "2019-08-30", "2019-08-31", "2019-09-01", "2019-09-03", "2019-09-04", "2019-09-09", "2019-09-10", "2019-09-12", "2019-09-14", "2019-09-15", "2019-09-16", "2019-09-17", "2019-09-18", "2019-09-19", "2019-09-20", "2019-09-21", "2019-09-22", "2019-09-23", "2019-09-24", "2019-09-25", "2019-09-26", "2019-09-27", "2019-09-28", "2019-09-29", "2019-09-30", "2019-10-01", "2019-10-04", "2019-10-08", "2019-10-09", "2019-10-10", "2019-10-14", "2019-10-15", "2019-10-17", "2019-10-18", "2019-10-19", "2019-10-20", "2019-10-23", "2019-10-24", "2019-10-25", "2019-10-26", "2019-10-27", "2019-10-28", "2019-10-29", "2019-10-30", "2019-10-31", "2019-11-01", "2019-11-02", "2019-11-03", "2019-11-04", "2019-11-05", "2019-11-06"],
        // y轴
        // 数据意义：开(open)，收(close)，最低(lowest)，最高(highest)
        "y": [
            [1000.23, 1000.23, 1000.23, 1000.23],
            [1000.23, 1000.23, 1000.23, 1000.23],
            [1000.23, 1000.23, 1000.23, 1000.23],
            [1000.23, 1000.23, 1000.23, 1000.23],
            [1000.23, 1000.23, 1000.23, 1000.23],
            [1143.12, 1143.12, 1143.12, 1143.12],
            [1143.12, 1143.12, 1143.12, 1143.12],
            [974.25, 974.25, 974.25, 974.25],
            [1143.12, 1143.12, 1143.12, 1143.12],
            [1199.0, 1199.0, 1199.0, 1199.0],
            [1039.2, 1039.2, 1039.2, 1039.2],
            [1039.2, 1039.2, 1039.2, 1039.2],
            [735.2, 1039.2, 735.2, 1039.2],
            [1039.2, 1039.2, 1039.2, 1039.2],
            [1039.2, 1039.2, 1039.2, 1039.2],
            [1039.2, 1039.2, 1039.2, 1039.2],
            [1039.2, 1039.2, 1039.2, 1039.2],
            [799.2, 799.2, 799.2, 799.2],
            [999.0, 999.0, 999.0, 999.0],
            [955.0, 955.0, 859.5, 955.0],
            [999.0, 955.0, 955.0, 999.0],
            [955.0, 955.0, 955.0, 955.0],
            [899.1, 899.1, 899.1, 899.1],
            [899.1, 899.1, 899.1, 899.1],
            [899.1, 899.1, 899.1, 899.1],
            [899.1, 899.1, 899.1, 899.1],
            [799.1, 799.1, 799.1, 799.1],
            [899.1, 899.1, 899.1, 899.1],
            [899.1, 899.1, 899.1, 899.1],
            [899.1, 899.1, 899.1, 899.1],
            [899.1, 899.1, 899.1, 999.0],
            [999.0, 999.0, 999.0, 999.0],
            [999.0, 799.0, 799.0, 999.0],
            [999.0, 799.0, 799.0, 999.0],
            [799.0, 799.0, 799.0, 799.0],
            [799.0, 799.0, 799.0, 799.0],
            [799.0, 799.0, 799.0, 799.0],
            [699.1, 699.1, 699.1, 699.1],
            [799.0, 699.1, 699.1, 799.0],
            [879.1, 979.0, 879.1, 979.0],
            [999.0, 979.0, 979.0, 999.0],
            [999.0, 999.0, 999.0, 999.0],
            [999.0, 999.0, 999.0, 999.0],
            [999.0, 939.0, 939.0, 999.0],
            [849.15, 849.15, 849.15, 849.15],
            [849.15, 939.0, 849.15, 939.0],
            [939.0, 939.0, 939.0, 939.0],
            [865.35, 865.35, 865.35, 865.35],
            [865.35, 865.35, 865.35, 865.35],
            [799.2, 799.2, 799.2, 799.2],
            [865.35, 865.35, 865.35, 865.35],
            [865.35, 849.15, 849.15, 865.35],
            [865.35, 865.35, 849.15, 865.35],
            [865.35, 865.35, 865.35, 865.35],
            [865.35, 865.35, 865.35, 865.35],
            [799.2, 799.2, 799.2, 799.2],
            [865.35, 719.2, 719.2, 865.35],
            [778.73, 865.35, 778.73, 865.35],
            [799.2, 799.2, 799.2, 799.2],
            [649.35, 799.15, 649.35, 799.15],
            [799.15, 799.15, 799.15, 799.15],
            [849.15, 999.0, 849.15, 999.0],
            [849.15, 849.15, 849.15, 849.15],
            [849.15, 849.15, 849.15, 849.15],
            [849.15, 849.15, 849.15, 849.15]
        ],
        "good": 602,
    }
    for(var i = 0 ; i < settings.x.length ; i++) {
        settings.tips.push("tips:"+i+i+i+i+i);
    }
    window.build_good_chart(settings);
}

})();







