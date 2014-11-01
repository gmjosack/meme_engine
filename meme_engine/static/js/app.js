(function() {

    var clamp = function(num, min, max){
        return Math.min(Math.max(num, min), max);
    }

    var lerp = function(start, end, fraction){
        return start + fraction * (end - start)
    }

    app = angular.module("memeEngine", ["ngRoute"]);

    app.config(function($interpolateProvider){
        $interpolateProvider.startSymbol("[[");
        $interpolateProvider.endSymbol("]]");
    })
    .config(function($logProvider){
        $logProvider.debugEnabled(true);
    })
    .config(function($locationProvider) {
        $locationProvider.html5Mode({
            enabled: true,
            requireBase: false
        });
    })
    .config(function($routeProvider) {
        $routeProvider
        .when("/", {
            templateUrl: "/static/templates/memes.html",
            controller: "MemesController"
        })
        .when("/meme", {
            templateUrl: "/static/templates/memes.html",
            controller: "MemesController"
        })
        .when("/meme/:meme_id", {
            templateUrl: "/static/templates/meme.html",
            controller: "MemeController"
        })

        .when("/meme/:meme_id/delete", {
            templateUrl: "/static/templates/meme-delete.html",
            controller: "MemeDeleteController"
        })
        .when("/template", {
            templateUrl: "/static/templates/templates.html",
            controller: "TemplatesController"
        })
        .when("/template/:template_id", {
            templateUrl: "/static/templates/template.html",
            controller: "TemplateController"
        })
        .when("/add_template", {
            templateUrl: "/static/templates/template-add.html",
            controller: "TemplateAddController"
        })
        .when("/create_meme", {
            templateUrl: "/static/templates/meme-create.html",
            controller: "MemeCreateController"
        })
        .otherwise({redirectTo: "/"});
    });

    app.controller("MemesController", [
            "$scope", "$http", "$location",
            function($scope, $http, $location) {

        $scope.memes = null;
        $scope.search = _.defaults($location.search(), {
            limit: 20,
            offset: 0
        });

        $scope.vote = function(meme, score) {
            // If You're clicking on something you've already voted for
            // then unvote for it.
            if (meme.score === score) {
                score = 0;
            }

            meme.score = score;
            $http.post("/api/meme/" + meme.id + "/vote", {"score": score}).success(function(data){
                meme.votes_up = data.data.votes_up;
                meme.votes_down = data.data.votes_down;
            });
        };

        $http.get("/api/meme", {params: $scope.search}).success(function(data){
            $scope.memes = data.data.memes;
        });

    }]);

    app.controller("MemeController", [
            "$scope", "$http", "$routeParams",
            function($scope, $http, $routeParams) {

        $scope.meme = null;
        $scope.showDelete = false;
        $scope.comment = "";
        $scope.comments = null;
        $scope.meme_id = $routeParams.meme_id;

        $http.get("/api/meme/" + $scope.meme_id).success(function(data){
            $scope.meme = data.data.meme;
            $scope.showDelete = data.data.show_delete;
        });

        $http.get("/api/meme/" + $scope.meme_id + "/comments").success(function(data){
            $scope.comments = data.data.comments;
        });

    }]);

    app.controller("MemeDeleteController", [
            "$scope", "$http", "$routeParams",
            function($scope, $http, $routeParams) {
        $scope.meme_id = $routeParams.meme_id;
    }]);

    app.controller("TemplatesController", [
            "$scope", "$http", "$location",
            function($scope, $http, $location) {

        $scope.search = _.defaults($location.search(), {
            limit: 20,
            offset: 0
        });
        $scope.templates = [];

        $http.get("/api/template", {params: $scope.search}).success(function(data){
            $scope.templates = data.data.templates;
        });

    }]);

    app.controller("TemplateController", [
            "$scope", "$http", "$routeParams",
            function($scope, $http, $routeParams) {

        $scope.template = null;
        $scope.template_id = $routeParams.template_id;

        $http.get("/api/template/" + $scope.template_id).success(function(data){
            $scope.template = data.data.template;
        });
    }]);


    app.controller("TemplateAddController", [
            "$scope", "$http",
            function($scope, $http) {
    }]);


    app.controller("MemeCreateController", [
            "$scope", "$http", "$location",
            function($scope, $http, $location) {


        $scope.errMsg = null;
        $scope.uploading = false;
        $scope.memeImage = new Image();
        $scope.memeCanvas = document.getElementById("meme-canvas");
        $scope.templates = null;
        $scope.selectedTemplate = null;
        $scope.texts = {
            topText: "",
            bottomText: "",
        };

        $scope.$watch("selectedTemplate", function(newV, oldV) {
            if (!newV) return;
            $scope.setSrc(newV);
        });

        var x, y;
        var context = $scope.memeCanvas.getContext('2d');
        var getFontSize = function(width, height, text){
            var maxHeight = height / 8;
            var minHeight = height / 12;

            var fontSize = lerp(maxHeight, minHeight, text.length * 5 / width);

            return clamp(fontSize, minHeight, maxHeight);
        };

        $http.get("/api/template?all=1").success(function(data){
            $scope.templates = data.data.templates;

            var search = $location.search();
            if (!search.key) return;

            var template = _.find($scope.templates, function(template){
                return template.key === search.key;
            });
            if (!template) return;

            $scope.selectedTemplate = template;
        });

        $scope.writeText = function() {
            context.drawImage($scope.memeImage, 0, 0);
            new CanvasTextWrapper($scope.memeCanvas, $scope.texts.topText, {
                font: getFontSize($scope.memeCanvas.width, $scope.memeCanvas.height, $scope.texts.topText) + 'px Impact',
                paddingY: 10,
                textAlign: "center",
                verticalAlign: "top",
                strokeText: true
            });
            new CanvasTextWrapper($scope.memeCanvas, $scope.texts.bottomText, {
                font: getFontSize($scope.memeCanvas.width, $scope.memeCanvas.height, $scope.texts.bottomText) + 'px Impact',
                paddingY: 10,
                textAlign: "center",
                verticalAlign: "bottom",
                strokeText: true
            });
        }

        $scope.setSrc = function(template){
            $scope.memeImage.src = "/image?key=" + template.key;
        };

        $scope.uploadMeme = function() {
            if (!$scope.selectedTemplate) return;

            $scope.uploading = true;

            var canvasData = $scope.memeCanvas.toDataURL();
            data = {
                texts: $scope.texts,
                image: canvasData,
                template: $scope.selectedTemplate
            }

            $http.post("/api/meme", data).success(function(data){
                window.location.href = "/meme/" + data.data.id;
            }).error(function(data, status, headers){
                $scope.errMsg = "Failed to upload: " + status
                $scope.uploading = false;
            });

        };

        $scope.memeImage.onload = function(){
            $scope.memeCanvas.width = $scope.memeImage.width;
            $scope.memeCanvas.height = $scope.memeImage.height;

            context.drawImage($scope.memeImage, 0, 0);
            context.fillStyle = 'white';
            context.strokeStyle = 'black';
            context.lineWidth = 2;
            $scope.writeText();
        };

    }]);

    app.filter('int', function() {
        return function(input) {
            return parseInt(input, 10);
        };
    });

})();
