/* global jQuery */
/* eslint-disable no-unused-vars, object-shorthand, no-implicit-globals, no-console */

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

        this._getFirst();
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
    
    M.prototype._getFirst = function(){
        for(var item in this.items){
            $.getJSON(
                dbPath, 
                {
                    key: this.key,
                    username: this.username,
                    action: "get"
                },
                function(item, data){
                    if(data.status == "fetched-item"){
                        this.items[item] = data.item;
                    }
                }.bind(this, (' ' + item).slice(1))
            );
        }
    };

    M.prototype.getNext = function(){
        var nextItem = this.items.next;

        $.getJSON(
            dbPath, 
            {
                key: this.key,
                username: this.username,
                action: "get"
            }, 
            function(data){
                if(data.status == "fetched-item") {
                    this.items.previous = this.items.current;
                    this.items.current = this.items.next;
                    this.items.next = data.item;
                } else {
                    console.log(data);
                }
            }.bind(this)
        );
        
        return nextItem;
    };

    M.prototype.saveAndGetNext = function(sentiment, ambiguous){
        sentiment = sentiment || false;
        ambiguous = ambiguous || false;
        if(!sentiment) {
            console.log("no sentiment specified, item not saved");
            return false;
        }

        $.extend(
            this.items.current,
            {
                sentiment: sentiment,
                ambiguous: ambiguous
            }
        );
        
        $.getJSON(
            dbPath, 
            {
                key: this.key,
                username: this.username,
                action: "save",
                sentiment: this.items.previous.sentiment,
                ambiguous: this.items.previous.ambiguous,
                token: this.items.previous.token
            },
            function(data){
                console.log(data);
            }
        );

        return this.getNext();
    };
    
    M.prototype.getPrevious = function(){
        this.items.next = this.items.current;
        this.items.current = this.items.previous;
        return this.items.current;
    };
    
    window.M = M;

}(jQuery));
