// -----------------------------------------------

function tableToJson(table) {
    var TYPE=0;
    var NAME=1;
    var MODIFIED=2;
    var SIZE=3;

    var data = [];

    var headers = [];
    for (var i=0; i<table.rows[0].cells.length; i++) {
        headers[i] = table.rows[0].cells[i].innerHTML;
    }
    console.assert(headers[NAME]=='Name');
    console.assert(headers[MODIFIED]=='Last modified');
    console.assert(headers[SIZE]=='Size');

    for (var i=1; i<table.rows.length; i++) {

        var tableRow = table.rows[i];

        var fa_name=tableRow.cells[TYPE].getAttribute("data-faname" );
        var name_td=tableRow.cells[NAME];
        var link_element = name_td.firstChild;
        var link = link_element.href;
        var name = link_element.firstChild.data;
        var modified_raw_html=tableRow.cells[MODIFIED].innerHTML;
        var size_raw_html=tableRow.cells[SIZE].innerHTML;

        var modifiedi = parseFloat(modified_raw_html); // in seconds
        if (modifiedi >= 0) {
            modifiedi = new Date(modifiedi*1000); // convert to msec
        } else {
            modifiedi = null;
        }
        var size = parseInt(size_raw_html);
        if (isNaN(size)) {
            size = -1;
        }

        var rowData = {name:name,
                       fa_name:fa_name,
                       link:link,
                       lastmodified:modifiedi,
                       size:size};

        data.push(rowData);
    }

    return data;
}

// -----------------------------------------------

var filters = angular.module('filters', []);

filters.filter('humanSize', function () {
    return function (numBytes, index) {
        if(typeof(numBytes)!=='number') return '';
        if(isNaN(numBytes)) return '';
        if(numBytes==null) return '';
        if(numBytes < 0) return '';
        if(numBytes == 0) return 0;
        if(numBytes < 1024) return (numBytes + " bytes");
        var s = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'];
        var e = Math.floor(Math.log(numBytes) / Math.log(1024));
        return (numBytes / Math.pow(1024, Math.floor(e))).toFixed(2) + " " + s[e];
    }
});

filters.filter('humanDate', function () {
    return function (date, format) {
        if(date==null) return '';
        if(isNaN(date)) return '';
        return date.toString();
    }
});

var app = angular.module('app', ['filters']);

app.controller('MainCtrl', function($scope) {
  var table = document.getElementById("static_site_index_html_table");
  var json_data = tableToJson(table);

  $scope.orderByField = 'name';
  $scope.reverseSort = false;

  $scope.data = {files:json_data};
});


angular.element(document).ready(function () {
  // Remove the static HTML index.
  var frameid = document.getElementById("static_site_index_html_index");
  frameid.parentNode.removeChild(frameid);

  var frameid = document.getElementById("static_site_index_js_index");
  frameid.style.display="block";
  frameid.style.visibility="visible";
});
