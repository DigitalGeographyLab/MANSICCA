/* global jQuery, M, m, mansiccaKey */
/* eslint-disable no-unused-vars, object-shorthand */

(function ($) {
    "use strict";

    $(document).ready(function(){

       /* Manage keyboard shortcuts for 
        * sentiments:
        *
        * … [X] [C] [V] [B] [N] [M] … (bottom row of keyboard)
        *    |   |   |   |   |   |
        *    |   |    \ /    |   +- positive
        *    |   |     |     +- positive (ambigous)
        *    |   |     +- neutral
        *    |   +- negative (ambigous)
        *    +- negative
        *
        */
        $(window)
            .keydown(function(e){ 
                switch(e.which){
                    case 88:
                        /* Xx */
                        $("controls button.negative").click().addClass("active");
                        break;
                    case 67:
                        /* Cc */
                        $("controls button.negativeAmbiguous").click().addClass("active");
                        break;
                    case 86:
                    case 66:
                        /* Vv Bb */
                        $("controls button.neutral").click().addClass("active");
                        break;
                    case 78:
                        /* Nn */
                        $("controls button.positiveAmbiguous").click().addClass("active");
                        break;
                    case 77:
                        /* Mm */
                        $("controls button.positive").click().addClass("active");
                        break;
                    default:
                        break;
                }
            })
            .keyup(function(e){
                $("controls button").removeClass("active");
            });

        /* Catch the actual button events
         */
        $("controls button").click(function(){
            if(window.m){
                var sentiment = false;
                var ambiguous = false;
    
                var classes = $(this).attr("class");

                if((classes.indexOf("back") > -1)){
                    if(!(classes.indexOf("disabled") > -1)){
                        if(m.items.previous.photo){
                            m.getPrevious();
                        }
                        $(this).addClass("disabled");
                    }
                } else {
    
                    if(classes.indexOf("positive") > -1){
                        sentiment = "positive";
                    } else if(classes.indexOf("neutral") > -1){
                        sentiment = "neutral";
                    } else if(classes.indexOf("negative") > -1){
                        sentiment = "negative";
                    } else if(classes.indexOf("skipped") > -1){
                        sentiment = "skipped";
                    }
        
                    if(classes.indexOf("Ambiguous") > -1){
                        ambiguous = true;
                    }
        
                    if(sentiment){
                        m.saveAndGetNext(
                            sentiment, 
                            ambiguous
                        );
                        $("controls button.back.disabled").removeClass("disabled");
                    }
                }
            }
        });


        /* Create an M object as soon as a username
         * is entered.
         */
        $("username input").on("keypress", function(e){
            if(e.keyCode == 13){
                var username = $(this).val();
                if(username && this.validity.valid){
                    $(this).prop("readonly", "readonly");
                    $("username").addClass("inactive");
            
                    window.m = new M(
                        $("content").get(0),
                        false,
                        username
                    );

                    localStorage.setItem("mansicca-username", username);
                }
            }
        });

        /* Check if we have a saved username, 
         * prefill the username input
         */
        var username = localStorage.getItem("mansicca-username");
        if(username){
            $("username input").val(username);
        }

        /* Click on hidden username -> change it
         */
        $("body").on("click", "username.inactive input", function() {
            $(this)
                .prop("readonly", false)
                .focus()
                .parent()
                    .removeClass("inactive");
        });

        /* save the last annotation when the 
         * user leaves the page 
         */
        $(window).bind('beforeunload', function(){
            if(window.m){
                m.saveAndGetNext(true);
            }
        });

    });
}(jQuery));
