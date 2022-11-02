$(document).ready(function (e) {


Highcharts.chart('project', {
    chart: {
        type: 'bar'
    },
    title: {
        text: 'Projects'
    },
    subtitle: {
        text: 'Year wise projects information'
    },
     credits: {
    enabled: false
  },
    xAxis: {
        categories: ['2018', '2019', '2020']
    },
    yAxis: {
        min: 0,
        title: {
            text: ''
        }
    },
    legend: {
        reversed: true
    },
    plotOptions: {
        series: {
            stacking: 'normal'
        }
    },
    series: [{
        name: 'UG',
        data: [5, 3, 4]
    }, {
        name: 'PG',
        data: [2, 2, 3]
    }, {
        name: 'PHD',
        data: [3, 4, 4]
    }]
});
 });