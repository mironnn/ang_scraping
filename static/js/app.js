// 'use strict';

// Declare app level module which depends on views, and components
angular.module('work_app', [])
    .run(['$rootScope', function ($rootScope) {
        $rootScope.pam = true;
    // $http.get('/my', data)
    //     .success(data, status, headers, config)
    }]);