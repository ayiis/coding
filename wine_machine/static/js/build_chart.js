// https://www.echartsjs.com/zh/option.html#series-candlestick
!(function(){

window.build_good_chart = function(settings) {
    var downColor = '#aaa';  // e00
    var downBorderColor = '#aaa'; // 900
    var upColor = '#ddd';   // ef3
    var upBorderColor = '#ddd';  // aa3

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
            scale: true,
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
                        borderColor0: downBorderColor
                    }
                },
                markLine: {
                    symbol: "none",
                    data: [{
                        yAxis: settings.good,
                        name: '好价',
                        lineStyle: {
                            normal: {
                                color: "green",
                                width: 1,
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
                        color: "red",
                        opacity: 0.5,
                        type: "dashed",
                    }
                }
            },
        ],
    };

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
                return params.seriesName + ": " + params.value;
            }
            var last_index = params['dataIndex'] - 1;
            var chajia = 0;
            if (last_index >= 0) {
                chajia = (params.data[3] - settings.y[last_index][2]).toFixed(2);
            }
            var text = [params.data[3] + (chajia>=0?'<i style="color:'+upColor+'"> +':'<i style="color:'+downColor+'"> ') + chajia + '</i>'];
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

var settings = {
    "ele": $('#ffff')[0],
    // x轴
    "x": ["190801", "190802", "190803", "190804", "190805", "190806"],
    // y轴
    "y": [
        // 数据意义：开(open)，收(close)，最低(lowest)，最高(highest)
        [1,2,1,2],
        [2,2,2,2],
        [2,4,3,6],
        [4,2,1,4],
        [2,5,2,6],
        [5,6,2,6],
    ],
    "good": 4.2,
}

window.build_good_chart(settings);

})();

console.log(1);













