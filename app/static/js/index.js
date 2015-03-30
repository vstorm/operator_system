$(document).ready(function () {
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });
    var server = $("[name='server']").val();
    var interval = $("[name='interval']").val();
    resource(server, interval);

    $(".change").click(function () {
        var server = $("[name='server']").val();
        var interval = $("[name='interval']").val();
        resource(server, interval);
    });
});

Date.prototype.subHours = function (h) {
    this.setHours(this.getHours() - h);
    return this;
}

Date.prototype.subDays = function (d) {
    this.setDate(this.getDate() - d);
    return this;
}


function resource(server, interval) {
    var now = new Date();
    var ago = new Date(now);
    var now_timestamp = parseInt(now.getTime() / 1000);
    var ago_timestamp;
    var ago_t;
    var resolution;
//    var categories = new Array();
    var title;
    if (interval == 'hour') {
        ago = ago.subHours(1);
        title = 'hour';
        resolution = '300';
    }
    else if (interval == 'day') {
        ago = ago.subDays(1);
        title = 'day'
        resolution = "1800";
    }
    else if (interval == 'week') {
        ago = ago.subDays(7);
        title = 'week'
        resolution = 432000;
    }
    ago_t = ago.getTime();
    ago_timestamp = parseInt(ago_t) / 1000

    $.ajax({
        url: "/server_resource",
        type: 'post',
        traditional: true,
        data: {
            'start_time': ago_timestamp,
            'end_time': now_timestamp,
            'server': server,
            'resolution': resolution
        },
        dataType: 'json',
        success: function (data) {
            load(ago_t, data['data']['load'], title, server, resolution);
            memory(ago_t, data['data']['memory'], title, server, resolution);
            cpu(ago_t, data['data']['cpu'], title, server, resolution);
        }
    });

}

function load(ago_timestamp, data, title, server, resolution) {
    $('#system-load').highcharts({
        title: {
            text: title + ' System Load',
            x: -20 //center
        },
//        subtitle: {
//            text: 'Source: WorldClimate.com',
//            x: -20
//        },
        xAxis: {
            align: 'left',
            type: "datetime", labels: { formatter: function () {
//                if(resolution==432000)
//                    return Highcharts.dateFormat("%H:%M", this.value);
//                else{
//                    return Highcharts.dateFormat("%D", this.value);
//                }
                d = new Date(this.value)
                if (resolution != 432000)
                    return d.getHours() + ":" + d.getMinutes();
                else {
                    return d.getDate();
                }
            }}
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Load Average'
            },
            plotLines: [
                {

                    value: 0,
                    color: '#808080'
                }
            ]
        },
        tooltip: {
//                    valueDecimals: 2,
//                    valueSuffix: '°C'
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [
            {
                name: server,
                data: data,
                pointStart: ago_timestamp,
//                pointInterval: 60 * 5 * 1000
                pointInterval: resolution * 1000
            }
        ]
    });
}


function memory(ago_timestamp, data, title, server, resolution) {
    $('#memory').highcharts({ chart: { type: 'area' }, title: { text: title + ' Memory Used' }, xAxis: { type: "datetime", labels: { formatter: function () {
        d = new Date(this.value)
        if (resolution != 432000)
            return d.getHours() + ":" + d.getMinutes();
        else {
            return d.getDate();
        }
    } } }, yAxis: { title: { text: 'Percentage' }
    }, tooltip: { pointFormat: 'use <b>{point.y:,.0f}</b> percent memory' }, plotOptions: { area: { pointStart: ago_timestamp, pointInterval: resolution * 1000, marker: { enabled: false, symbol: 'circle', radius: 2, states: { hover: { enabled: true } } } } }, series: [
        { name: server, data: data }
    ] });
}

function cpu(ago_timestamp, data, title, server, resolution) {
    $('#cpu').highcharts({ chart: { type: 'area' }, title: { text: title + " Cpu Used" }, xAxis: { type: "datetime", labels: { formatter: function () {
        d = new Date(this.value)
        if (resolution != 432000)
            return d.getHours() + ":" + d.getMinutes();
        else {
            return d.getDate();
        }
    } } }, yAxis: { title: { text: 'Percent' }, labels: { formatter: function () {
        return this.value;
    } } }, tooltip: { pointFormat: 'use <b>{point.y:,.0f}</b> percent cpu' }, plotOptions: { area: { pointStart: ago_timestamp, pointInterval: resolution * 1000, marker: { enabled: false, symbol: 'circle', radius: 2, states: { hover: { enabled: true } } } } }, series: [
        { name: server, data: data }
//        { name: 'USSR/Russia', data: [null, null, null, null, null, null, null , null , null , null, 5, 25, 50, 120, 150, 200, 426, 660, 869, 1060, 1605, 2471, 3322, 4238, 5221, 6129, 7089, 8339, 9399, 10538, 11643, 13092, 14478, 15915, 17385, 19055, 21205, 23044, 25393, 27935, 30062, 32049, 33952, 35804, 37431, 39197, 45000, 43000, 41000, 39000, 37000, 35000, 33000, 31000, 29000, 27000, 25000, 24000, 23000, 22000, 21000, 20000, 19000, 18000, 18000, 17000, 16000 ] }
    ] });
}