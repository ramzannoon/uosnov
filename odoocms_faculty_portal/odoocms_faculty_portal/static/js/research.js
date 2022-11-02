$(document).ready(function (e) {
Highcharts.chart('publication', {
    chart: {
        type: 'column',
        options3d: {
            enabled: true,
            alpha: 10,
            beta: 25,
            depth: 70
        }
    },
    title: {
        text: 'Publications'
    },
    subtitle: {
        text: 'Year wise publication information'
    },
    plotOptions: {
        column: {
            depth: 25
        }
    },
    credits: {
    enabled: false
  },
    xAxis: {
        categories: ['2018', '2019', '2020'],
        labels: {
            skew3d: true,
            style: {
                fontSize: '16px'
            }
        }
    },
    yAxis: {
        title: {
            text: null
        }
    },
    series: [{
        name: 'Journals',
        data: [0, 0, 2]
    },
     {
        name: 'Conference papers',
        data: [0, 0, 1],
        stack: 'male'
    }]
});
Highcharts.chart('patent', {
    chart: {
        type: 'cylinder',
        options3d: {
            enabled: true,
            alpha: 15,
            beta: 15,
            depth: 50,
            viewDistance: 25
        }
    },
    title: {
        text: 'Patents'
    },
     subtitle: {
        text: 'Year wise patents information'
    },
    credits: {
    enabled: false
  },
  xAxis: {
        categories: ['2018', '2019', '2020'],
        labels: {
            skew3d: true,
            style: {
                fontSize: '16px'
            }
        }
    },
    plotOptions: {
        series: {
            depth: 25,
            colorByPoint: true
        }
    },
    series: [{
        data: [0, 0, 1],
        name: 'Patents',
        showInLegend: true
    }]
});
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
        data: [5, 0, 1]
    }, {
        name: 'PG',
        data: [2, 2, 1]
    }, {
        name: 'PHD',
        data: [3, 4, 1]
    }]
});
 });