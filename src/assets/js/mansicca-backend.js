/* global jQuery */
/* eslint-disable no-unused-vars, object-shorthand, no-implicit-globals */

(function ($) {
    "use strict";

    var M = function(container, user){
        this.container = container || false;
        this.user = user || "";
    };
    
    M.Item = function(caption, photo) {
        this.caption = caption || "";
        this.photo = photo || false;
        this._preloadPhoto();
    }
    
    M.Item._preloadPhoto = function() {
        if(this.photo){
            var photo = new Image();
            photo.src = this.photo;
        }
    }
    
    M.items = {
        previous: new M.Item(),
        current:  new M.Item(),
        next:     new M.Item()
    }
    
    M.prototype.getNext = function(){
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
