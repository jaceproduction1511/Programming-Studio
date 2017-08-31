/* ------------------------------------------------------------------------- */
/* Lair Crushers 2: The Wumpus Strikes Back                                  */
/* Developers:                                                               */
/*     - Aaron Ayrault                                                       */
/*     - Andrew Kirfman                                                      */
/*     - Cheng Chen                                                          */
/*     - Cuong Do                                                            */
/*                                                                           */
/* File: ./static/js/pages/host.js                                           */
/* ------------------------------------------------------------------------- */


/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

// Setup Player Information
var host_parser = document.createElement('a');
var entered_game_name = "";
var current_mode_choice = "";
host_parser.href = window.location.href;
var host_addr = host_parser.host;
var player_name = host_parser.search.replace("?", "");

// Preload All Hover & Active Images
Preload(
    '/static/interface_elements/host_a_game/back_hover.png',
    '/static/interface_elements/host_a_game/collaborative_active.png',
    '/static/interface_elements/host_a_game/collaborative_hover.png',
    '/static/interface_elements/host_a_game/host_hover.png',
    '/static/interface_elements/host_a_game/player_vs_player_active.png',
    '/static/interface_elements/host_a_game/player_vs_player_hover.png'
);


/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_host";
var ws = new WebSocket(socket_addr);

ws.onopen = function() 
{
    ws.send("PlayerName:" + player_name);
};

ws.onmessage = function(message) 
{
    var received_msg = message.data;
    if(received_msg.indexOf("Ping") >= 0)
    {
        ws.send("Pong");
    }
    else if(received_msg.indexOf("ValidationSuccess") >= 0)
    {
        ws.send("SetupGame:" + entered_game_name + ":" + current_mode_choice
            + ":" + player_name);
    }
    else if(received_msg.indexOf("ValidationFailure") >= 0)
    {
        var invalid_game_name_text = document.createElement('invalid_game_name');
        invalid_game_name_text.setAttribute('class', 'invalid_game_name');
        document.body.appendChild(invalid_game_name_text);
        invalid_game_name_text.innerHTML = "Invalid Name or Name Exists!  Try Again!";
    }
    else if(received_msg.indexOf("CleanUpSuccessful") >= 0)
    {
        window.location.href = "/";
    }
    else if(received_msg.indexOf("SetupSuccess") >= 0)
    {
        window.location.href = "/difficulty_selection?" + player_name;
    }
};

ws.onclose = function() 
{  };


/* ------------------------------------------------------------------------- */
/* Miscalaneous Functions                                                    */
/* ------------------------------------------------------------------------- */

function UpdateModeChoice(new_choice)
{
    current_mode_choice = new_choice;
}

function VerifyGameName() 
{
    if(current_mode_choice == "")
    {
        return;
    }
    
    entered_game_name = document.getElementById('game_name').value;
    if(entered_game_name.indexOf(';') >= 0 || entered_game_name.indexOf(':') >= 0)
    {
        var invalid_game_name_text = document.createElement('invalid_game_name');
        invalid_game_name_text.setAttribute('class', 'invalid_game_name');
        document.body.appendChild(invalid_game_name_text);
        invalid_game_name_text.innerHTML = "Invalid Name or Name Exists!  Try Again!";                    
    }
    else
    {
        ws.send("ValidateGameName:" + entered_game_name);
    }
}