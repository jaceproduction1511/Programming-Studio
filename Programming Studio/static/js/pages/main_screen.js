/* ------------------------------------------------------------------------- */
/* Lair Crushers 2: The Wumpus Strikes Back                                  */
/* Developers:                                                               */
/*     - Aaron Ayrault                                                       */
/*     - Andrew Kirfman                                                      */
/*     - Cheng Chen                                                          */
/*     - Cuong Do                                                            */
/*                                                                           */
/* File: ./static/js/pages/main_screen.js                                    */
/* ------------------------------------------------------------------------- */


/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

var host_parser = document.createElement('a');
var requested_action = "";
var entered_name = "";
host_parser.href = window.location.href;
var host_addr = host_parser.host;

// Preload All Hover & Active Images
Preload(
	"/static/interface_elements/main_screen/help_hover.png",
	"/static/interface_elements/main_screen/host_a_new_game_hover.png",
    "/static/interface_elements/main_screen/join_existing_game_hover.png"
);


/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_main";
var ws = new WebSocket(socket_addr);

ws.onopen = function() 
{  };

ws.onmessage = function(received_message) 
{
    if(received_message.data.indexOf("Success") >= 0)
    {
        if(requested_action.indexOf("host") >= 0)
        {
            window.location.href = "/host?" + entered_name;
        }
        else if(requested_action.indexOf("join") >= 0)
        {
            window.location.href = "/join?" + entered_name;
        }
    }
    else if(received_message.data.indexOf("Failure") >=0)
    {
        var invalid_name_text = document.createElement('invalid_name');
        invalid_name_text.setAttribute('class', 'invalid_name');
        document.body.appendChild(invalid_name_text);
        invalid_name_text.innerHTML = "Invalid Name or Name Exists!  Try Again!";
    }
};

ws.onclose = function() 
{  };


/* ------------------------------------------------------------------------- */
/* Miscellaneous Functions                                                   */
/* ------------------------------------------------------------------------- */

function VerifyName(action) 
{
    requested_action = action;
    var temp_name = document.getElementById('host_name');
    entered_name = temp_name.value;
    if(entered_name.indexOf(';') >= 0 || entered_name.indexOf(':') >= 0)
    {
        var invalid_name_text = document.createElement('invalid_name');
        invalid_name_text.setAttribute('class', 'invalid_name');
        document.body.appendChild(invalid_name_text);
        invalid_name_text.innerHTML = "Invalid Name or Name Exists!  Try Again!";                        
    }
    else
    {
        ws.send("ValidateName:" + entered_name);
    }
}