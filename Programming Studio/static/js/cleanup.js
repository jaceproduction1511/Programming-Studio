/* ------------------------------------------------------------------------- */
/* Lair Crushers 2: The Wumpus Strikes Back                                  */
/* Developers:                                                               */
/*     - Aaron Ayrault                                                       */
/*     - Andrew Kirfman                                                      */
/*     - Cheng Chen                                                          */
/*     - Cuong Do                                                            */
/*                                                                           */
/* File: ./static/js/pages/cleanup.js                                        */
/* ------------------------------------------------------------------------- */


/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

var host_parser = document.createElement('a');
var entered_game_name = "";
var current_mode_choice = "";
host_parser.href = window.location.href;
var host_addr = host_parser.host;
var player_name = host_parser.search.replace("?", "");
host_parser.search;


/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_cleanup";
var ws = new WebSocket(socket_addr);

ws.onopen = function()
{
    ws.send("Name:" + player_name);
};

ws.onmessage = function(received_message)
{
    if(received_message.data.indexOf("Ping") >= 0)
    {
        ws.send("Pong");
    }
    else if(received_message.data.indexOf("CleanUpSuccessful") >=0)
    {
        window.location.href = "/";
    }
    else if(received_message.data.indexOf("Name:") >=0)
    {
        var game_name = received_message.replace("Name:", "");
        ws.send("CleanUp:" + game_name);
    }
};

ws.onclose = function()
{  };