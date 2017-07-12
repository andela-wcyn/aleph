import aleph from '../aleph';

aleph.factory('Articles', ['$q', '$http', '$location',
    function($q, $http, $location) {

  var getArticles = function() {
    var dfd = $q.defer();
    var spreadsheetID = "1SN02GD7b4d2dqrbgfrWE2bclSorXYF5E6UqhNFjaWig";
    $http.get('https://spreadsheets.google.com/feeds/list/' +
        spreadsheetID + '/od6/public/values?alt=json').then(function(res) {
      dfd.resolve(res.data.feed);
    }, function(err) {
      dfd.reject(err);
    });
    return dfd.promise;
  };

  return {
    get: getArticles
  };
}]);
