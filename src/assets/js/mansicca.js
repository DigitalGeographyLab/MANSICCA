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
                }
            })
            .keyup(function(e){
               $("controls button").removeClass("active");
            });

    });
}(jQuery));


