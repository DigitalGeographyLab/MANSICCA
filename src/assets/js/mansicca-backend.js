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
        this.username = username || "anonymous";

        if(this.container){
            this.container = $(this.container);
        }

        if(!this.key){
            if(window.location.hash.length > 1){
                this.key = window.location.hash.substring(1);
            }
        }

        this._getFirst();
    };
    
    M.Item = function(options) {
        this._options = $.extend(
            {
                caption: "",
                photo: false,
                token: "",
                url: "",
                stylesheet: "instagram"
            },
            options
        );

        this.caption = this._options.caption;
        this.photo = this._options.photo;
        this.token = this._options.token;
        this.url = this._options.url;
        this.stylesheet = this._options.stylesheet;

        if(this.photo && this.photo.substring(0,4) != "http"){
            this.photo = path + "../data/" + this.photo[0] + "/" + this.photo;
        }
        this._preloadPhoto(this.photo);
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
        $.getJSON(
            dbPath, 
            {
                key: this.key,
                username: this.username,
                action: "get"
            },
            function(data){
                if(data.status == "fetched-item"){
                    this.items.next = new M.Item(data.item);
                    this.getNext.bind(this)();
                }
            }.bind(this)
        );
    };

    M.prototype._updateContainer = function(item) {
        item = item || this.items.current;
        this.container
            .removeClass()
            .addClass(item.stylesheet)
            .find("img")
                .removeAttr("src")
                .attr(
                    "src", 
                    item.photo
                )
                .end()
            .find("div.caption")
                .text(item.caption);
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
                if(data.status == "fetched-item") {
                    delete this.items.previous
                    this.items.previous = this.items.current

                    delete this.items.current
                    this.items.current = this.items.next

                    delete this.items.next
                    this.items.next = new M.Item(data.item)

                    this._updateContainer.bind(this)(); 
                } else {
                    console.log(data);
                }
            }.bind(this)
        );
    };

    M.prototype.saveAndGetNext = function(sentiment, ambiguous){
        sentiment = sentiment || false;
        ambiguous = ambiguous || false;
        if(sentiment) {
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
                    this.getNext();
                }.bind(this)
            );
        }
    };
    
    M.prototype.getPrevious = function(){
        delete this.items.next;
        this.items.next = this.items.current;

        delete this.items.current;
        this.items.current = this.items.previous;

        delete this.items.previous;
        this.items.previous = new M.Item();

        this._updateContainer();
    };
    
    window.M = M;

}(jQuery));
