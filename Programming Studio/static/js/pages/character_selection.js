/* ------------------------------------------------------------------------- */
/* Lair Crushers 2: The Wumpus Strikes Back                                  */
/* Developers:                                                               */
/*     - Aaron Ayrault                                                       */
/*     - Andrew Kirfman                                                      */
/*     - Cheng Chen                                                          */
/*     - Cuong Do                                                            */
/*                                                                           */
/* File: ./static/js/pages/character_selection.js                            */
/* ------------------------------------------------------------------------- */


/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

// Setup Player Information
var host_parser = document.createElement('a');
var entered_game_name = "";
var current_class_choice = "";
host_parser.href = window.location.href;
var host_addr = host_parser.host;
var player_name = host_parser.search.replace("?", "");

// Preload All Hover & Active Images
Preload(
	"/static/interface_elements/character_selection/back_hover.png",
	"/static/interface_elements/character_selection/hunter_active.png",
    "/static/interface_elements/character_selection/hunter_hover.png",
    "/static/interface_elements/character_selection/prospector_active.png",
    "/static/interface_elements/character_selection/prospector_hover.png",
    "/static/interface_elements/character_selection/scout_active.png",
    "/static/interface_elements/character_selection/scout_hover.png",
    "/static/interface_elements/character_selection/start_hover.png",
    "/static/interface_elements/character_selection/survivor_active.png",
    "/static/interface_elements/character_selection/survivor_hover.png"
);


/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

// Open Websocket
var socket_addr = "ws://" + host_addr + "/ws_character";
var ws = new WebSocket(socket_addr);

ws.onopen = function()
{  
    ws.send("PlayerName:" + player_name);
};

ws.onmessage = function(message)
{
    var received_message = message.data;

    if(received_message.indexOf("Ping") >= 0)
    {
        ws.send("Pong");
    }
    else if(received_message.indexOf("CharacterSet") >= 0)
    {
        window.location.href = "/easy_game?" + player_name;
    }
    else if(received_message.indexOf("ReturnHost") >= 0)
    {
        window.location.href = "/difficulty_selection?" + player_name;
    }
    else if(received_message.indexOf("ReturnJoin") >= 0)
    {
        window.location.href = "/join?" + player_name;
    }
};

ws.onclose = function()
{  };


/* ------------------------------------------------------------------------- */
/* Miscalaneous Functions                                                    */
/* ------------------------------------------------------------------------- */

function ContinueScreen()
{
    if(current_class_choice != "")
    {
        ws.send("SetCharacter:" + player_name + ":" + current_class_choice);
    }
}