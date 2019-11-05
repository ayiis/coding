!(function() {
    var option = {
        title: {
            text: '阶梯瀑布图',
            subtext: 'From ExcelHome',
            sublink: 'http://e.weibo.com/1341556070/Aj1J2x5a5'
        },
        tooltip : {
            trigger: 'axis',
            axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            },
            formatter: function (params) {
                var tar;
                if (params[1].value != '-') {
                    tar = params[1];
                }
                else {
                    tar = params[0];
                }
                return tar.name + '<br/>' + tar.seriesName + ' : ' + tar.value;
            }
        },
        legend: {
            data:['支出','收入']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type : 'category',
            splitLine: {show:false},
            data :  function (){
                var list = [];
                for (var i = 1; i <= 11; i++) {
                    list.push('11月' + i + '日');
                }
                return list;
            }()
        },
        yAxis: {
            type : 'value'
        },
        series: [
            {
                name: '辅助',
                type: 'bar',
                stack: '总量',
                itemStyle: {
                    normal: {
                        // show: false,
                        // barBorderColor: 'rgba(0,0,0,0)',
                        // color: 'rgba(0,0,0,0)'
                    },
                    emphasis: {
                        // barBorderColor: 'rgba(0,0,0,0)',
                        // color: 'rgba(0,0,0,0)'
                    }
                },
                data: [0, 900, 1245, 1530, 1376, 1376, 1511, 1689, 1856, 1495, 1292]
            },
            {
                name: '收入',
                type: 'bar',
                stack: '总量',
                label: {
                    normal: {
                        show: true,
                        position: 'top'
                    }
                },
                data: [900, 345, 393, '-', '-', 135, 178, 286, '-', '-', '-']
            },
            {
                name: '支出',
                type: 'bar',
                stack: '总量',
                label: {
                    normal: {
                        show: true,
                        position: 'bottom'
                    }
                },
                data: ['-', '-', '-', 108, 154, '-', '-', '-', 119, 361, 203]
            }
        ]
    };

    function build() {
        var chart = echarts.init($('#ffff')[0]);
        chart.clear();
        chart.setOption(option);
        // chart.on('click', function(params) {
        //     if(settings["click_callback"]) {
        //         settings["click_callback"](params);
        //     }
        // });
    }
    build();

})();

(function() {
    window.build_chart2 = {
        init: function(settings) {
            // 通用地图显示设置
            var option = {
                tooltip : {
                    trigger: 'axis'
                },
                legend: {
                    data: settings["area_list"]
                },
                toolbox: {
                    show : false,
                    feature : {
                        mark : {show: true},
                        dataView : {show: true, readOnly: false},
                        magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                        restore : {show: true},
                        saveAsImage : {show: true}
                    }
                },
                calculable : true,
                xAxis : [
                    {
                        type : 'category',
                        boundaryGap : false,
                        data : settings["date_list"]
                    }
                ],
                yAxis : [
                    {
                        scale: true,
                        type : 'value'
                    }
                ],
                series : settings["data"]
            };
            var eleid = settings["ele"].getAttribute('id');
            if(!window.build_chart2[eleid]) {
                window.build_chart2[eleid] = echarts.init(settings["ele"]);
            }
            var chart = window.build_chart2[eleid];

            chart.clear();
            chart.setOption(option);
            chart.on('click', function(params) {
                if(settings["click_callback"]){
                    settings["click_callback"](params);
                }
            });
        }
    };
});
