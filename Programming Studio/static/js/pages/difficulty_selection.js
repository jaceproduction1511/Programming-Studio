/* ------------------------------------------------------------------------- */
/* Lair Crushers 2: The Wumpus Strikes Back                                  */
/* Developers:                                                               */
/*     - Aaron Ayrault                                                       */
/*     - Andrew Kirfman                                                      */
/*     - Cheng Chen                                                          */
/*     - Cuong Do                                                            */
/*                                                                           */
/* File: ./static/js/pages/difficulty_selection.js                           */
/* ------------------------------------------------------------------------- */


/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

// Setup Player Information
var host_parser = document.createElement('a');
host_parser.href = window.location.href;
var host_addr = host_parser.host;
var player_name = host_parser.search.replace("?", "");
var entered_difficulty = "";

// Preload All Hover & Active Images
Preload(
	"/static/interface_elements/difficulty_selection/back_hover.png",
	"/static/interface_elements/difficulty_selection/explorer_active.png",
    "/static/interface_elements/difficulty_selection/explorer_hover.png",
    "/static/interface_elements/difficulty_selection/next_hover.png",
    "/static/interface_elements/difficulty_selection/vlad_tepes_active.png",
    "/static/interface_elements/difficulty_selection/vlad_tepes_hover.png",
    "/static/interface_elements/difficulty_selection/wuss_active.png",
    "/static/interface_elements/difficulty_selection/wuss_hover.png"
);


/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

// Open Websocket
var socket_addr = "ws://" + host_addr + "/ws_difficulty";
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
    else if(received_message.indexOf("CleanUpSuccessful") >=0)
    {
        window.location.href = "/host?" + player_name;
    }
    else if(received_message.indexOf("DifficultySet") >= 0)
    {
        window.location.href = "/character_selection?" + player_name;
    }
};

ws.onclose = function()
{  };


/* ------------------------------------------------------------------------- */
/* Miscalaneous Functions                                                    */
/* ------------------------------------------------------------------------- */

function RecordDifficulty()
{
    if(entered_difficulty != "")
    {
        ws.send("Difficulty:" + player_name + ":" + entered_difficulty);
    }
}