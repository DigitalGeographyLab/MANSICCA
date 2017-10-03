/* global jQuery */
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
                        mansiccaKey,
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


    });
}(jQuery));
