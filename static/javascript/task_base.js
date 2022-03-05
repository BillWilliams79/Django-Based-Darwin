
$(document).ready(
    function() {

        //
        // app grid setup on load, runs once per page load
        //
        check_set_grid_sizes();

        console.log('tfs');
        toggleFullScreen();

        //
        // register: app grid setup on resize
        //
        $(window).resize(check_set_grid_sizes);

    });

//
// app grid setup library function used in $(document).ready
//
function check_set_grid_sizes() {

    //
    // extract class list from item1 and determine current size based on class name applied.
    // never found any jquery to assist with this.
    //
    var item1_size = 'not_found';
    var classList = document.getElementById('item1').className.split(/\s+/);

    for (var i = 0; i < classList.length; i++) {
        if (classList[i] === 'item1') {
            item1_size = 'large';
            break;
        } else if (classList[i] === 'item1sm') {
            item1_size = 'small';
            break;
        }
    }
    
    //
    // check for mismatched document width and applied size classes
    // when document width is >= 768 it is "large" and the set_divs_large
    // classes are applied to the grid items.
    //
    if ($(document).width() >= 768) {
        //
        // Doc is large, adjust if not large
        //
        if (item1_size != 'large') {
            
            var div_list = $('div').filter(function() {
                return this.id.match(/item[0-9]/);
                })

            set_divs_large(div_list);
        }

    } else {
        //
        // Doc is small, adjust if larage
        //
        if (item1_size != 'small') {
            
            var div_list = $('div').filter(function() {
                return this.id.match(/item[0-9]/);
                })
            set_divs_small(div_list);
        }
    }

    //
    // pair of helper functions to set divs large/small.
    // I could have used one function and toggle, but prefer these always
    // toggle affirmatively together.
    //
    function set_divs_large(div_list) {
        for (div of div_list) {
            $("#" + div.id).addClass(div.id);
            $("#" + div.id).removeClass(div.id + "sm");
        }
    }

    function set_divs_small(div_list) {
        for (div of div_list) {
            $("#" + div.id).removeClass(div.id);
            $("#" + div.id).addClass(div.id + "sm");
            console.log('SUCCESS SMALL');
        }
    }
}

function toggleFullScreen() {
    var doc = window.document;
    var docEl = doc.documentElement;
  
    var requestFullScreen = docEl.requestFullscreen || docEl.mozRequestFullScreen || docEl.webkitRequestFullScreen || docEl.msRequestFullscreen;
    var cancelFullScreen = doc.exitFullscreen || doc.mozCancelFullScreen || doc.webkitExitFullscreen || doc.msExitFullscreen;
  
    if(!doc.fullscreenElement && !doc.mozFullScreenElement && !doc.webkitFullscreenElement && !doc.msFullscreenElement) {
      requestFullScreen.call(docEl);
      console.log('requesting fs');
    }
    else {
      cancelFullScreen.call(doc);
    }
  }

