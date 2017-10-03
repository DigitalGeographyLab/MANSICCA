/* global jQuery */
/* eslint-disable no-unused-vars, object-shorthand, no-implicit-globals */

(function ($) {
    "use strict";

    var path = window.location.href;
    path = path.substr(0, path.lastIndexOf("/") + 1);
    path += $("script").last().attr("src");
    path = path.substr(0, path.lastIndexOf("/") + 1);

    var dbPath = path + "../db/mansicca.py";

    var M = function(container, key, username){
        this.container = container || false;
        this.key = key || false;
        this.username = username || "";

        this.getNext();
    };
    
    M.Item = function(caption, photo) {
        this.caption = caption || "";
        this.photo = photo || false;
        this._preloadPhoto();
    }
    
    M.Item.prototype._preloadPhoto = function() {
        if(this.photo){
            var photo = new Image();
            photo.src = this.photo;
        }
    }
    
    M.prototype.items = {
        previous: new M.Item(),
        current:  new M.Item(),
        next:     new M.Item()
    }
    
    M.prototype.getNext = function(){
        $.getJSON(
            dbPath, 
            {
                key: this.key,
                username: this.username,
                action: "get"
            }, 
            function(data){
                console.log(data);
            }
        );


        // returns already cached next item, 
        // loads another one into cache
    };
    
    M.prototype.saveAndGetNext = function(){
        // saves previous (!) item, 
        // moves current item to previous position in stack
        // then calls getNext()
    };
    
    M.prototype.getPrevious = function(){
        // discards cached next item, 
        // puts current item into next-item position in stack,
        // loads previous
    };
    
    window.M = M;

}(jQuery));
