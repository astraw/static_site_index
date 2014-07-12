var filters = angular.module('filters', []);

filters.filter('humanSize', function () {
    return function (bytes, index) {
        if(bytes==null) return '';
        if(bytes <= 0) return 0;
        var s = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'];
        var e = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, Math.floor(e))).toFixed(2) + " " + s[e];
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
  $scope.orderByField = 'Name';
  $scope.reverseSort = false;

  $scope.data = entries;
});


angular.element(document).ready(function () {
  // Remove the static HTML index.
  var frameid = document.getElementById("static_site_index_html_index");
  frameid.parentNode.removeChild(frameid);

  var frameid = document.getElementById("static_site_index_js_index");
  frameid.style.display="block";
  frameid.style.visibility="visible";
});
