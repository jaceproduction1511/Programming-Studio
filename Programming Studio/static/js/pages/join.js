/* ------------------------------------------------------------------------- */
/* Lair Crushers 2: The Wumpus Strikes Back                                  */
/* Developers:                                                               */
/*     - Aaron Ayrault                                                       */
/*     - Andrew Kirfman                                                      */
/*     - Cheng Chen                                                          */
/*     - Cuong Do                                                            */
/*                                                                           */
/* File: ./static/js/pages/join.js                                           */
/* ------------------------------------------------------------------------- */


/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

var host_parser = document.createElement('a');
var game_name = "";
host_parser.href = window.location.href;
var host_addr = host_parser.host;
var player_name = host_parser.search.replace("?", "");

var btns = [];
var text_elements = [];
var difficulty_elements = [];
var counter = 0;

// Preload All Hover & Active Images
Preload(
	"/static/interface_elements/join_a_game/back_button_hover.png",
	"/static/interface_elements/join_a_game/join_button_hover.png",
    "/static/interface_elements/join_a_game/refresh_hover.png"
);


/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_join";
var ws = new WebSocket(socket_addr);

ws.onopen = function()
{
    ws.send("Name:" + player_name);
};

ws.onmessage = function(message)
{
    var received_msg = message.data;
    if(received_msg.indexOf("Ping") >= 0)
    {
        ws.send("Pong");
        ws.send("RequestActiveGames")
    }
    else if(received_msg.indexOf("ClearList") >= 0)
    {
        Refresh();
    }
    else if(received_msg.indexOf("Game:") >= 0)
    {
        // Calculate Positions
		counter = counter + 1;
        var info = received_msg.split(";");
        var name = info[0].replace("Game:", "").replace("%20", " ");
        var toppos = 31 + counter * 3;

        // Buttons
        var btn = document.createElement("BUTTON");
        var n = document.createTextNode(name);
        btn.setAttribute("name", name);
        btn.appendChild(n);
        btn.setAttribute("onclick", 'game_name = name');
        btn.setAttribute('style', 'top: ' + toppos + '%; left: 23%; width: 10%; position: fixed;');
		btns.push(btn);
        document.body.appendChild(btns[counter - 1]);

        // Game Modes
        var mode = info[1].replace("Mode:", "");
        var mode_text = document.createElement("P");
		var m = document.createTextNode(mode);
		mode_text.appendChild(m);
		mode_text.setAttribute('style', 'top: ' + toppos + '%; left: 45%; position: fixed; color: white;');
		text_elements.push(mode_text);
		document.body.appendChild(text_elements[counter - 1]);

        // Difficulties
        var diff = info[2].replace("Difficulty:", "");
        var diff_text = document.createElement('P');
		var d = document.createTextNode(diff);
		diff_text.appendChild(d);
		diff_text.setAttribute('style', 'top: ' + toppos + '%; left: 60%; position: fixed; color: white;');
        difficulty_elements.push(diff_text);
        document.body.appendChild(difficulty_elements[counter - 1]);
    }
    else if(received_msg.indexOf("Failure") >=0)
    {
        var err = document.createElement("P");
        var t = document.createTextNode("Game is full! Try joining another game!");
        err.appendChild(t);
        err.style.color = "#FF0000";
        err.style.top = toppos+ "70%";
        err.style.left = "37%";
        //err.style.font-size = "1.4vw";
        document.body.appendChild(err);
    }
    else if(received_msg.indexOf("JoinSuccessful") >= 0)
    {
        window.location.href = "/character_selection?" + player_name;
    }
    else if(received_msg.indexOf("CleanUpSuccessful") >= 0)
    {
        window.location.href = "/";
    }
};

ws.onclose = function()
{  };


/* ------------------------------------------------------------------------- */
/* Miscellaneous Functions                                                   */
/* ------------------------------------------------------------------------- */

function Refresh()
{
	counter = 0;
	for (var i = 0; i<btns.length; i++)
	{
	    btns[i].parentNode.removeChild(btns[i]);
	}
	for (var i = 0; i<text_elements.length; i++)
	{
	    text_elements[i].parentNode.removeChild(text_elements[i]);
	}
	for (var i = 0; i<difficulty_elements.length; i++)
	{
	    difficulty_elements[i].parentNode.removeChild(difficulty_elements[i]);
	}

	btns = [];
	text_elements = [];
	difficulty_elements = [];
}
