/* ------------------------------------------------------------------------- */
/* Lair Crushers 2: The Wumpus Strikes Back                                  */
/* Developers:                                                               */
/*     - Aaron Ayrault                                                       */
/*     - Andrew Kirfman                                                      */
/*     - Cheng Chen                                                          */
/*     - Cuong Do                                                            */
/*                                                                           */
/* File: ./static/js/pages/easy_game.js                                      */
/* ------------------------------------------------------------------------- */


/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

String.prototype.replaceAll = function(search, replacement)
{
    var target = this;
    return target.split(search).join(replacement);
};

// Recover Player Information
var host_parser = document.createElement('a');
host_parser.href = window.location.href;
var host_addr = host_parser.host;
var host_name = host_parser.search;
var player_name = host_name.replace("?", "").replace("%20", " ");
var game_mode = "";
var other_player_name = "";

var committed_move = "";
var prev_move = "";
var move_mutex = false;

var visible_player = "";
var x = 0;
var y = 0;
// Basic Game Window Data
var horizontal_diff = 5.44;
var vertical_diff = 10.1;
// Containers for custom created elements
var current_percepts = [];
var opponents = [];
var btns = [];

// Cpmtaomer for clickable buttons
var clickable_buttons = [];
var player_position = [-1, -1];
var player_elements = [];

// Don't allow the user to perform any actions if another player hasn't joined.
var ready_to_play = false;
var is_scout = false;

// Notifications Box
var notification_box = document.createElement('div');
notification_box.setAttribute('class', 'notifications');
notification_box.setAttribute('id', 'notification_box');
document.body.appendChild(notification_box);

// Add Initial Notifications
AddNotification("Welcome to the game " + player_name + "!", 'rgb(240, 244, 33)');
AddNotification("Waiting for other player...", 'rgb(57, 176, 219)');

// Preload All Hover & Active Images
Preload(
    "/static/interface_elements/easy/move_arrow_gray_up.png",
    "/static/interface_elements/easy/move_arrow_gray_down.png",
    "/static/interface_elements/easy/move_arrow_gray_left.png",
    "/static/interface_elements/easy/move_arrow_gray_right.png",
    "/static/interface_elements/easy/move_arrow_red_up.png",
    "/static/interface_elements/easy/move_arrow_red_down.png",
    "/static/interface_elements/easy/move_arrow_red_left.png",
    "/static/interface_elements/easy/move_arrow_red_right.png",
    "/static/interface_elements/easy/cancel_hover.png",
    "/static/interface_elements/easy/fire_hover.png",
    "/static/interface_elements/easy/scout_hover.png"
);

//audios
var AudioPaths = [];
AudioPaths.push("/static/interface_elements/audio/radioactive_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/weight_of_love_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/what_does_the_fox_say_background_song.mp3");
AudioPaths.push("/static/interface_elements/audio/anime_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/get_lucky_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/bohemian_rhapsody_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/back_in_black_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/crazy_train_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/cantina_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/rick_roll_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/to_hell_and_back_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/cliffs_of_gallipoli_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/entertainer_background_sound.mp3");
AudioPaths.push("/static/interface_elements/audio/weight_of_love_long_background_sound.mp3");


/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_easy";
var ws = new WebSocket(socket_addr);

ws.onopen = function()
{
    ws.send("PlayerName:"  + player_name);
    ws.send("GameStart:"   + player_name);
    //ws.send("GetGameMode:" + player_name);
};

ws.onmessage = function(event)
{
    var message = event.data;

    if(message.indexOf("Ping") >= 0)
    {
        ws.send("Pong");
    }
    
    else if(message.indexOf("ForceShowOtherPlayer:") >= 0)
    {
        message = message.replace("ForceShowOtherPlayer:", "");
        opponents.push(message);
        if (game_mode == "collaborative")
        {
            ws.send("GetOtherPlayer:" + player_name);
        }
        
        // background music
        var audio=Math.floor(Math.random() * (AudioPaths.length));
        audio=new Audio(AudioPaths[audio]);
        audio.loop = true;
        audio.play();
        }
    
    else if(message.indexOf("Joined:") >= 0)
    {
        message = message.replace("Joined:", "");
        opponents.push(message);
        AddNotification(message + " has joined the game!", 'white');
    }

    else if(message.indexOf("Message:") >= 0)
    {
        message = message.replace("Message:", "");
        AddMessage(message, 'white');
        
        var audio = new Audio('/static/interface_elements/audio/chat_sound.mp3');
        audio.play();
    }

    else if(message.indexOf("InitialLocation") >=0)
    {
        ready_to_play = true;

        ws.send("GetArrowsCount:" + player_name);
        ws.send("GetLivesCount:"  + player_name);
        ws.send("GetPerceptions:" + player_name);
        if(is_scout)
        {
            ws.send("GetAbilityCount:" +  player_name);
        }

        message = message.replace("InitialLocation:", "");
        message = message.split(",");
        var x_pos = parseInt(message[0]);
        var y_pos = parseInt(message[1]);
        player_position[0] = parseInt(x_pos);
        player_position[1] = parseInt(y_pos);
        AddPlayer(player_name, x_pos, y_pos);
        if (game_mode == "collaborative")
        {
            AddPlayer2(visible_player, x, y);
        }
        AddVisibleDoor(0, 0);
        DrawClickableElements('move');
    }

    else if(message.indexOf("GameMode:", "") >=0)
    {
        message = message.replace("GameMode:", "").replace("%20", " ");
        game_mode = message.toString();
    }

    else if(message.indexOf("OtherPlayer:", "") >=0)
    {
        message = message.replace("OtherPlayer:", "").replace("%20", " ");
        message = message.split(":");
        visible_player = message[0];
        x = parseInt(message[1]);
        y = parseInt(message[2]);
        if (game_mode == "collaborative")
        {
            ws.send("GetPerceptions:" + visible_player);
            ws.send("GetPerceptions:" + player_name);
            AddPlayer2(visible_player, x, y);
        }
        ws.send("GetPerceptions:" + player_name);
        
    }

    else if(message.indexOf("Class") >= 0)
    {
        message = message.replace("Class:", "");
        if(message.indexOf("scout") >= 0)
        {
            is_scout = true;
        }
        else
        {
            document.body.removeChild(document.getElementById('ability_button'));
            document.body.removeChild(document.getElementById('ability_cancel'));
        }
    }

    else if(message.indexOf("Valid") >= 0)
    {
        var wait_element = document.createElement('p');
        wait_element.setAttribute('style', 'color: rgb(57, 176, 219); position: relative; ' +
        'word-wrap: break-word; padding: 0; margin: 0; font-size: 1vw;');
        wait_element.setAttribute('id', 'wait_message');
        wait_element.innerHTML = "Waiting for other players...";
        UpdateScroll('notification_box');
        document.getElementById('notification_box').appendChild(wait_element);
    }

    else if(message.indexOf("InvalidMove") >= 0)
    {
        committed_move = "";
        move_mutex = false;
    }

    else if(message.indexOf("ApplyMove") >= 0)
    {
        // Remove waiting message
        var wait_message = document.getElementById('wait_message');
        document.getElementById('notification_box').removeChild(wait_message);

        MovePlayer(committed_move);
        prev_move = "";
        //old_move = committed_move;
        committed_move = "";
        move_mutex = false;

        //get perceptions
        ws.send("GetLivesCount:" +  player_name);
        if (game_mode == "collaborative")
        {
            //add new player2 at location
            ws.send("GetOtherPlayer:" + player_name);

            //remove old player2 at location
            RemovePlayer(visible_player)
            ws.send("GetPerceptions:" + visible_player);
            ws.send("GetPerceptions:" + player_name);
        }
        ws.send("GetPerceptions:" + player_name);
    }

    else if(message.indexOf("SetPerceptions") >= 0)
    {
        SetPerceptions(message);
    }

    else if(message.indexOf("PickedUp") >= 0)
    {
        ws.send("GetArrowsCount:" + player_name);
        ws.send("GetLivesCount:" +  player_name);
        if(is_scout)
        {
            ws.send("GetAbilityCount:" +  player_name);
        }
    }

    else if(message.indexOf("RemoveElements") >= 0)
    {
        RemovePerceptions(message);
        ws.send("GetLivesCount:" + player_name);
    }

    else if(message.indexOf('Arrows') >= 0)
    {
        var test = document.getElementById('arrows_box');
        if(test == null)
        {
            var new_element = document.createElement('a');
            new_element.setAttribute('class', 'arrows_box');
            new_element.setAttribute('id', 'arrows_box');
            new_element.innerHTML = message.replace('ArrowsCount:', '');
            document.body.appendChild(new_element);
        }
        else
        {
            test.innerHTML = message.replace('ArrowsCount:', '');
        }
    }

    else if(message.indexOf('Lives') >= 0)
    {
        var test = document.getElementById('lives_box');
        if(test == null)
        {
            var new_element = document.createElement('a');
            new_element.setAttribute('class', 'lives_box');
            new_element.setAttribute('id', 'lives_box');
            new_element.innerHTML = message.replace('LivesCount:', '');
            document.body.appendChild(new_element);
        }
        else
        {
            test.innerHTML = message.replace('LivesCount:', '');
        }
    }

    else if(message.indexOf('Ability') >= 0)
    {
        var test = document.getElementById('ability_box');
        if(test == null)
        {
            var new_element = document.createElement('a');
            new_element.setAttribute('class', 'ability_box');
            new_element.setAttribute('id', 'ability_box');
            new_element.innerHTML = message.replace('AbilityCount:', '');
            document.body.appendChild(new_element);
        }
        else
        {
            test.innerHTML = message.replace('AbilityCount:', '');
        }
    }

    else if(message.indexOf('Died:') >= 0)
    {
        ws.send("GetLivesCount:" + player_name);
        var fate = message.replace("Died:", "");
        
        var audio;
        audio = new Audio('/static/interface_elements/audio/wilhelm_scream_sound.mp3');
        audio.play();

        if(fate.indexOf("StillAlive") >= 0)
        {
            move_mutex = false;
            var lives_box = document.getElementById('lives_box');
            lives_box.innerHTML = lives_box.innerHTML - 1;
        }
        else if(fate.indexOf("Dead") >= 0)
        {
            window.location.href = "/game_over" + host_name;
        }
    }

    else if(message.indexOf("WumpusDead:") >= 0)
    {
        var wumpus_position = message.replace("WumpusDead:", "").split(':');
        RemoveElement('wumpus', wumpus_position[0], wumpus_position[1]);
        
        var audio;
        audio = new Audio('/static/interface_elements/audio/wumpus_death_sound.mp3');
        audio.play();
    }

    else if(message.indexOf("Notification:") >= 0)
    {
        ws.send("GetLivesCount:" + player_name);
        message = message.replace("Notification:", "").split(':');
        AddNotification(message[1], message[0]);
        
    }

    else if(message.indexOf("Victory") >= 0)
    {
        window.location.href = "/victory" + host_name;
    }
};

ws.onclose = function()
{  };


/* ------------------------------------------------------------------------- */
/* Chat & Notifications                                                      */
/* ------------------------------------------------------------------------- */

function AddMessage(message, color)
{
    var new_element = document.createElement('p');
    new_element.setAttribute('style', 'color: ' + color + '; position: relative; ' +
        'word-wrap: break-word; padding: 0; margin: 0; font-size: 1vw;');
    message = message.split(':');
    new_element.innerHTML = '[' + message[0] + ']: ' +  message[1];
    document.getElementById('chat_out_box').appendChild(new_element);
    UpdateScroll('chat_out_box');
}

function AddNotification(message, color)
{
    var new_element = document.createElement('p');
    new_element.setAttribute('style', 'color: ' + color + '; position: relative; ' +
        'word-wrap: break-word; padding: 0; margin: 0; font-size: 1vw;');
    new_element.innerHTML = message;
    document.getElementById('notification_box').appendChild(new_element);
    UpdateScroll('notification_box');
    
    //handling what sound should be played
    var audio;
    audio = new Audio('/static/interface_elements/audio/notification_sound.mp3');
    audio.play();
}

function SendMessage()
{
    var temp_box = document.getElementById('chat_in_box');
    var message_data = temp_box.value;
    temp_box.value = "";
    AddMessage(player_name + ':' + message_data, 'rgb(57, 176, 219)');
    ws.send("NewMessage:" + player_name + ':' + message_data);
}

function UpdateScroll(div_name)
{
    var element = document.getElementById(div_name);
    element.scrollTop = element.scrollHeight;
}


/* ------------------------------------------------------------------------- */
/* Player Movement                                                           */
/* ------------------------------------------------------------------------- */

function CommitMove(move_direction)
{
    if(move_mutex == false)
    {
        var insert_left;
        var insert_top;
        
        if(move_direction == "up")
        {
            insert_left = 2.55 + player_position[0] * horizontal_diff;
            insert_top = 8.3 + (player_position[1] - 1) * vertical_diff;
            
            for(var i=0; i<player_elements.length; i++)
            {
                if(player_elements[i].id.indexOf('up') >= 0)
                {
                    player_elements[i].style = "background: url('static/interface_elements/easy/move_arrow_green_up.png'); height: 10%; cursor: pointer;"
                        + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left +  "%;";
                }
            }
        }
        else if(move_direction == "down")
        {
            insert_left = 2.55 + player_position[0] * horizontal_diff;
            insert_top = 8.3 + (player_position[1] + 1) * vertical_diff;
            
            for(var i=0; i<player_elements.length; i++)
            {
                if(player_elements[i].id.indexOf('down') >= 0)
                {
                    player_elements[i].style = "background: url('static/interface_elements/easy/move_arrow_green_down.png'); height: 10%; cursor: pointer;"
                        + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left +  "%;";
                }
            }            
        }
        else if(move_direction == "left")
        {
            insert_left = 2.55 + (player_position[0] - 1) * horizontal_diff;
            insert_top = 8.3 + player_position[1] * vertical_diff;
            
            for(var i=0; i<player_elements.length; i++)
            {
                if(player_elements[i].id.indexOf('left') >= 0)
                {
                    player_elements[i].style = "background: url('static/interface_elements/easy/move_arrow_green_left.png'); height: 10%; cursor: pointer;"
                        + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left +  "%;";
                }
            }
        }
        else if(move_direction == "right")
        {
            insert_left = 2.55 + (player_position[0] + 1) * horizontal_diff;
            insert_top = 8.3 + player_position[1] * vertical_diff;
            
            for(var i=0; i<player_elements.length; i++)
            {
                if(player_elements[i].id.indexOf('right') >= 0)
                {
                    player_elements[i].style = "background: url('static/interface_elements/easy/move_arrow_green_right.png'); height: 10%; cursor: pointer;"
                        + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left +  "%;";
                }
            }
        }
        
        committed_move = move_direction;
        ws.send("Validate:" + player_name + ':' + committed_move);
        move_mutex = true;
        ws.send("GetLivesCount:" + player_name);
    }
}

function MovePlayer(move_direction)
{
    var player_element = document.getElementById(player_name);
    var player_y_per = parseFloat(player_element.style.top.replace("%", ""), 10);
    var player_x_per = parseFloat(player_element.style.left.replace("%", ""), 10);

    if(move_direction == "up")
    {
        player_position[1] = player_position[1] - 1;
        player_element.style.top = (player_y_per - vertical_diff).toString() + "%";
    }
    else if(move_direction == "down")
    {
        player_position[1] = player_position[1] + 1;
        player_element.style.top = (player_y_per + vertical_diff).toString() + "%";
    }
    else if(move_direction == "left")
    {
        player_position[0] = player_position[0] - 1;
        player_element.style.left = (player_x_per - horizontal_diff).toString() + "%";
    }
    else if(move_direction == "right")
    {
        player_position[0] = player_position[0] + 1;
        player_element.style.left = (player_x_per + horizontal_diff).toString() + "%";
    }
    
    // Make arrows move with player
    DrawClickableElements('move');
    
}

function RemovePlayer(player_name_in)
{
    var player_element = document.getElementById(player_name_in);
    player_element.parentNode.removeChild(player_element);
}



/* ------------------------------------------------------------------------- */
/* Perception Updates                                                        */
/* ------------------------------------------------------------------------- */

function RemoveAll(element_type)
{
    var items_to_remove = [];
    var children = document.body.childNodes;
    for(var i=0; i<children.length; i++)
    {
        if(typeof(children[i].id) !== "undefined")
        {
            if(children[i].id.indexOf(element_type) >= 0 && children[i].id.indexOf('indicator') <= 0)
            {
                items_to_remove.push(children[i]);
            }
        }
    }
    for(var i=0; i<items_to_remove.length; i++)
    {
        items_to_remove[i].parentNode.removeChild(items_to_remove[i]);
    }
}

function RemoveElement(element_type, board_x, board_y)
{
    if(document.getElementById(element_type + board_x + ':' + board_y) != null)
    {
        if(element_type === "wumpus")
        {
            RemoveElement('smell', board_x + 1, board_y);
            RemoveElement('smell', board_x - 1, board_y);
            RemoveElement('smell', board_x, board_y + 1);
            RemoveElement('smell', board_x, board_y - 1);
        }

        var old_element = document.getElementById(element_type + board_x + ':' + board_y);
        old_element.parentNode.removeChild(old_element);
    }
}

function RemovePerceptions(perceptions_string)
{
    perceptions_string = perceptions_string.replace("RemoveElements:", "");
    current_percepts = perceptions_string.split(",");
    var playerx = parseInt(current_percepts[0]);
    var playery = parseInt(current_percepts[1]);

    if(current_percepts.indexOf('arrow') >= 0)
    {
        RemoveElement('arrow', playerx, playery);
    }
    if(current_percepts.indexOf('life_potion') >= 0)
    {
        RemoveElement('life_potion', playerx, playery);
    }
    if(current_percepts.indexOf('ability_potion') >= 0)
    {
        RemoveElement('ability_potion', playerx, playery);
    }
    if(current_percepts.indexOf('gold') >= 0)
    {
        RemoveElement('gold', playerx, playery);
    }
    if(current_percepts.indexOf('glitter') >= 0)
    {
        RemoveAll('glitter');
    }
    if (game_mode == "collaborative")
    {
        ws.send("GetPerceptions:" + visible_player);
        ws.send("GetPerceptions:" + player_name);
    }
}

function SetPerceptions(perceptions_string)
{
    perceptions_string = perceptions_string.replace("SetPerceptions:", "");
    current_percepts = perceptions_string.split(",");
    var playerx = current_percepts[0];
    var playery = current_percepts[1];

    if(current_percepts.indexOf('pit') >= 0)
    {
        AddVisiblePit(playerx, playery);
    }
    if(current_percepts.indexOf('wumpus') >= 0)
    {
        AddVisibleWumpus(playerx, playery);
    }
    if(current_percepts.indexOf('breeze') >= 0)
    {
        AddVisibleBreeze(playerx, playery);
    }
    if(current_percepts.indexOf('smell') >= 0)
    {
        AddVisibleSmell(playerx, playery);
    }
    if(current_percepts.indexOf('gold') >= 0)
    {
        AddVisibleGold(playerx, playery);
    }
    if(current_percepts.indexOf('glitter') >= 0)
    {
        AddVisibleGlitter(playerx, playery);
    }
    if(current_percepts.indexOf('arrow') >= 0)
    {
        AddVisibleArrow(playerx, playery);
    }
    if(current_percepts.indexOf('life_potion') >= 0)
    {
        AddVisibleLifePotion(playerx, playery);
    }
    if(current_percepts.indexOf('ability_potion') >= 0)
    {
        AddVisibleAbilityPotion(playerx, playery);
    }
    if(current_percepts.indexOf('door') >= 0)
    {
        AddVisibleDoor(playerx, playery);
        ws.send("CheckVictory:" + player_name);
    }
    if(current_percepts.indexOf('empty') >= 0)
    {
        AddVisibleEmpty(playerx, playery);
    }
    
    if(current_percepts.indexOf('footsteps') >= 0)
    {
        console.log("footstep trigered");
        AddNotification("you hear footstepas nearby", "yellow");
        
        var footstep_element = document.createElement('f');
        footstep_element.setAttribute('style', 'color: rgb(255, 255, 0); position: relative; ' +
        'word-wrap: break-word; padding: 0; margin: 0; font-size: 1vw;');
        footstep_element.setAttribute('id', 'footstep_element');
        footstep_element.innerHTML = "You hear footsteps nearby";
        UpdateScroll('notification_box');
        document.getElementById('notification_box').appendChild(footstep_element);
    }
    else
    {
        // Remove waiting message
        var footstep_element = document.getElementById('footstep_element');
        document.getElementById('notification_box').removeChild(footstep_element);
    }
}


/* ------------------------------------------------------------------------- */
/* Element Placement                                                         */
/* ------------------------------------------------------------------------- */

function AddPlayer(player_name, board_x, board_y)
{
    var new_player = document.createElement('img');
    new_player.setAttribute('src', 'static/interface_elements/universal/player_sprite.png');

    var insert_left = 2.14 + board_x * horizontal_diff;
    var insert_top = 8.3 + board_y * vertical_diff;

    new_player.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
        + 'width: 6%; height: 6%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
    new_player.setAttribute('id', player_name);
    document.body.appendChild(new_player);
}

function AddPlayer2(player_name, board_x, board_y)
{
    var new_player = document.createElement('img');
    new_player.setAttribute('src', 'static/interface_elements/universal/player2_sprite.png');

    var insert_left = 2.14 + board_x * horizontal_diff;
    var insert_top = 8.3 + board_y * vertical_diff;

    new_player.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
        + 'width: 6%; height: 6%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
    new_player.setAttribute('id', player_name);
    document.body.appendChild(new_player);  
}

function AddVisibleSmell(board_x, board_y)
{
    var check_existence = document.getElementById('smell' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_smell = document.createElement('img');
        new_smell.setAttribute('src', 'static/interface_elements/universal/smell.png');
        
        
        var insert_left = 3.2 + board_x * horizontal_diff;
        var insert_top = 6.5 + board_y * vertical_diff;

        new_smell.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 4%; height: 5%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_smell.setAttribute('id', 'smell' + board_x + ':' + board_y);
        document.body.appendChild(new_smell);
    }
}

function AddVisibleBreeze(board_x, board_y)
{
    var check_existence = document.getElementById('breeze' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_breeze = document.createElement('img');
        new_breeze.setAttribute('src', 'static/interface_elements/universal/breeze.png');

        //16.8 for center
        var insert_left = 4.3 + board_x * horizontal_diff;
        var insert_top = 13 + board_y * vertical_diff;

        new_breeze.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 8%; height: 9%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_breeze.setAttribute('id', 'breeze' + board_x + ':' + board_y);
        document.body.appendChild(new_breeze);
    }
}

function AddVisibleAbilityPotion(board_x, board_y)
{
    var check_existence = document.getElementById('ability_potion' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_ability_potion = document.createElement('img');
        new_ability_potion.setAttribute('src', 'static/interface_elements/universal/ability_potion_sprite.png');

        var insert_left = 2.14 + board_x * horizontal_diff;
        var insert_top = 10 + board_y * vertical_diff;

        new_ability_potion.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 1%; height: 1.5%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_ability_potion.setAttribute('id', 'ability_potion' + board_x + ':' + board_y);
        document.body.appendChild(new_ability_potion);
    }
}

function AddVisibleGlitter(board_x, board_y)
{
    var check_existence = document.getElementById('glitter' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_glitter = document.createElement('img');
        new_glitter.setAttribute('src', 'static/interface_elements/universal/glitter.png');

        var insert_left = -2 + board_x * horizontal_diff;
        var insert_top = 6 + board_y * vertical_diff;

        new_glitter.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 6%; height: 10%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_glitter.setAttribute('id', 'glitter' + board_x + ':' + board_y);
        document.body.appendChild(new_glitter);
    }
}

function AddVisibleLifePotion(board_x, board_y)
{
    var check_existence = document.getElementById('life_potion' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_life_potion = document.createElement('img');
        new_life_potion.setAttribute('src', 'static/interface_elements/universal/life_potion_sprite.png');

        var insert_left = 6 + board_x * horizontal_diff;
        var insert_top = 10 + board_y * vertical_diff;

        new_life_potion.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 1%; height: 1.5%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_life_potion.setAttribute('id', 'life_potion' + board_x + ':' + board_y);
        document.body.appendChild(new_life_potion);
    }
}

function AddVisibleArrow(board_x, board_y)
{
    var check_existence = document.getElementById('arrow' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_arrow = document.createElement('img');
        new_arrow.setAttribute('src', 'static/interface_elements/universal/arrow_sprite.png');

        var insert_left = 3 + board_x * horizontal_diff;
        var insert_top = 8.3 + board_y * vertical_diff;

        new_arrow.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 3.5%; height: 6%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_arrow.setAttribute('id', 'arrow' + board_x + ':' + board_y);
        document.body.appendChild(new_arrow);
    }
}

function AddVisibleEmpty(board_x, board_y)
{
    var check_existence = document.getElementById('empty' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_empty = document.createElement('p');
        var text_node = document.createTextNode("E");
        new_empty.appendChild(text_node);

        var insert_left = 4 + board_x * horizontal_diff;
        var insert_top = 8.3 + board_y * vertical_diff;

        new_empty.setAttribute('style', 'outline: none; border: none; cursor: pointer; font-size: 1vw;'
            + 'color: white; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_empty.setAttribute('id', 'empty' + board_x + ':' + board_y);
        document.body.appendChild(new_empty);
    }
}

function AddVisibleDoor(board_x, board_y)
{
    var check_existence = document.getElementById('door'+ board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_door = document.createElement('img');
        new_door.setAttribute('src', 'static/interface_elements/universal/door_sprite.png');

        var insert_left = 2.75 + board_x * horizontal_diff;
        var insert_top = 8 + board_y * vertical_diff;

        new_door.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 3.5%; height: 6%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_door.setAttribute('id', 'door' + board_x + ':' + board_y);
        document.body.appendChild(new_door);
    }
}

function AddVisibleGold(board_x, board_y)
{
    var check_existence = document.getElementById('gold' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_gold = document.createElement('img');
        new_gold.setAttribute('src', 'static/interface_elements/universal/gold_sprite.png');

        var insert_left = 2.8 + board_x * horizontal_diff;
        var insert_top = 8.3 + board_y * vertical_diff;

        new_gold.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 3.5%; height: 6%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_gold.setAttribute('id', 'gold' + board_x + ':' + board_y);
        document.body.appendChild(new_gold);
    }
}

function AddVisiblePit(board_x, board_y)
{
    var check_existence = document.getElementById('pit' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_pit = document.createElement('img');
        new_pit.setAttribute('src', 'static/interface_elements/universal/pit_sprite.png');

        var insert_left = 3 + board_x * horizontal_diff;
        var insert_top = 8.3 + board_y * vertical_diff;

        new_pit.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 4%; height: 5%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_pit.setAttribute('id', 'pit' + board_x + ':' + board_y);
        document.body.appendChild(new_pit);
    }
}

function AddVisibleWumpus(board_x, board_y)
{
    var check_existence = document.getElementById('wumpus' + board_x + ':' + board_y);
    if(check_existence === null)
    {
        var new_wumpus = document.createElement('img');
        new_wumpus.setAttribute('src', 'static/interface_elements/universal/wumpus_sprite.png');

        var insert_left = 2 + board_x * horizontal_diff;
        var insert_top = 8.3 + board_y * vertical_diff;

        new_wumpus.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 5%; height: 6%; position: fixed; left: ' + insert_left + '%; top: ' + insert_top + '%;');
        new_wumpus.setAttribute('id', 'wumpus' + board_x + ':' + board_y);
        document.body.appendChild(new_wumpus);
    }
}


/* ------------------------------------------------------------------------- */
/* Player Abilities                                                          */
/* ------------------------------------------------------------------------- */

function FireArrow(arrow_direction)
{
    ws.send("FireArrow:" + player_name + ':' + arrow_direction);
    ws.send("GetArrowsCount:" + player_name);
    ws.send("GetLivesCount:" + player_name);
    
    var test = document.getElementById('arrows_box');
    if (parseInt(test.innerHTML) > 0)
    {
        var audio = new Audio('/static/interface_elements/audio/minecraft_arrow_sound.mp3');
        audio.play();
    }
    DrawClickableElements('move');
}

function PickUp(player_object)
{
    ws.send("PickUp:" + player_name);
    ws.send("GetLivesCount:" + player_name);
    ws.send("GetPerceptions:" + player_name);
    if (game_mode == "collaborative")
    {
        ws.send("GetPerceptions:" + visible_player);
        ws.send("GetPerceptions:" + player_name);
    }
}

function ScoutActive()
{
    for(var cols = 0; cols < 13; cols++)
    {
        for(var rows = 0; rows < 9; rows++)
        {
            var btn = document.createElement("button");
            btn.setAttribute('background', 'static/interface_elements/universal/scout_select.png');
            var insert_left = 2.2 + cols * horizontal_diff;
            var insert_top = 7 + rows * vertical_diff;
            btn.setAttribute("onclick", 'Scouting(' + cols + ',' + rows + ')');
            btn.setAttribute('style', 'outline: none; border: none; cursor: pointer;'
            + 'width: 4.5%; height: 8%; position: fixed; opacity: 0.35; left: ' + insert_left + '%; top: ' + insert_top + '%;');
            btn.setAttribute('id', 'overlay' + cols + ':' + rows);
            document.body.appendChild(btn);
        }
    }
}

function CancelActive()
{

    for(var cols = 0; cols < 13; cols++)
        for(var rows = 0; rows < 9; rows++)
        {
            if(document.getElementById('overlay' + cols + ':' + rows) != null)
            {
                var old_element = document.getElementById('overlay' + cols + ':' + rows);
                old_element.parentNode.removeChild(old_element);
            }
        }
    
}

function FireActive()
{
    DrawClickableElements('fire');
}

function CancelFire()
{
    DrawClickableElements('move');
}

function Scouting (board_x, board_y)
{
    ws.send("Scouting:" + player_name + ',' + board_x + "," + board_y);
    CancelActive();
}


function DrawClickableElements(action_type)
{
    for(var i=0; i<player_elements.length; i++)
    {
        if(player_elements[i] !== null)
        {
            player_elements[i].parentNode.removeChild(player_elements[i]);
        }
    }
    player_elements = [];

    /* Clickable Pick-Up Box */
    var btn = document.createElement("button");
        
    var insert_left = 2.2 + player_position[0] * horizontal_diff;
    var insert_top = 7 + player_position[1] * vertical_diff;
    
    btn.setAttribute("onclick", "PickUp(player_name)");
    btn.setAttribute('style', 'outline: none; background: transparent; border: none; cursor: pointer; z-index: 10;'
        + 'width: 4.5%; height: 8%; position: fixed; opacity: 0; left: ' + insert_left + '%; top: ' + insert_top + '%;');
    btn.setAttribute('id', 'element' + player_position[0] + ':' + player_position[1]);
    document.body.appendChild(btn);
    player_elements.push(btn);    


    if(action_type == "move")
    {
        /* Up Arrow */
        if(player_position[1] > 0)
        {
            var btn = document.createElement("button");
            
            // NEEDS TO BE UPDATED
            var insert_left = 2.55 + player_position[0] * horizontal_diff;
            var insert_top = 8.3 + (player_position[1] - 1) * vertical_diff;
            
            btn.setAttribute("onclick", "CommitMove('up');")
            btn.style = "background: url('static/interface_elements/easy/move_arrow_gray_up.png'); height: 10%; cursor: pointer;"
                + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left +  "%;";
            btn.setAttribute('id', 'up' + player_position[0] + ':' + (player_position[1] - 1));
            document.body.appendChild(btn);
            player_elements.push(btn);
        }
        
        
        /* Down Arrow */
        if(player_position[1] < 8)
        {
            btn = document.createElement("button");
            
            // NEEDS TO BE UPDATED
            var insert_left = 2.55 + player_position[0] * horizontal_diff;
            var insert_top = 8.3 + (player_position[1] + 1) * vertical_diff;
            
            btn.setAttribute("onclick", "CommitMove('down');");
            btn.style = "background: url('static/interface_elements/easy/move_arrow_gray_down.png'); height: 10%; cursor: pointer;"
                + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left + "%;"
            btn.setAttribute('id', 'down' + player_position[0] + ':' + (player_position[1] + 1));
            document.body.appendChild(btn);
            player_elements.push(btn);
        }
        
        
        /* Left Arrow */
        if(player_position[0] > 0)
        {
            btn = document.createElement("button");
            
            // NEEDS TO BE UPDATED
            var insert_left = 2.55 + (player_position[0] - 1) * 5.44;
            var insert_top = 8.3 + player_position[1] * 10.1;
            
            btn.setAttribute("onclick", "CommitMove('left');");
            btn.style = "background: url('static/interface_elements/easy/move_arrow_gray_left.png'); height: 10%; cursor: pointer;"
                + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left + "%;"
            btn.setAttribute('id', 'left' + (player_position[0] - 1) + ':' + player_position[1]);
            document.body.appendChild(btn);
            player_elements.push(btn);
        }
        
        
        /* Right Arrow */
        if(player_position[0] < 12)
        {
            btn = document.createElement("button");
            
            // NEEDS TO BE UPDATED
            var insert_left = 2.55 + (player_position[0] + 1) * horizontal_diff;
            var insert_top = 8.3 + player_position[1] * vertical_diff;
            
            btn.setAttribute("onclick", "CommitMove('right')");
            btn.style = "background: url('static/interface_elements/easy/move_arrow_gray_right.png'); height: 10%; cursor: pointer;"
                + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left + "%;"
            btn.setAttribute('id', 'right' + (player_position[0] + 1) + ':' + player_position[1]);
            document.body.appendChild(btn);
            player_elements.push(btn);
        }
        
    }
    else if(action_type == "fire")
    {
        /* Up Arrow */
        if(player_position[1] > 0)
        {
            var btn = document.createElement("button");
            
            // NEEDS TO BE UPDATED
            var insert_left = 2.55 + player_position[0] * horizontal_diff;
            var insert_top = 8.3 + (player_position[1] - 1) * vertical_diff;
            
            btn.setAttribute("onclick", "FireArrow('up')");
            btn.style = "background: url('static/interface_elements/easy/move_arrow_red_up.png'); height: 10%; cursor: pointer;"
                + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left +  "%;";
            btn.setAttribute('id', 'element' + player_position[0] + ':' + (player_position[1] - 1));
            document.body.appendChild(btn);
            player_elements.push(btn);
        }
        
        
        /* Down Arrow */
        if(player_position[1] < 8)
        {
            btn = document.createElement("button");
            
            // NEEDS TO BE UPDATED
            var insert_left = 2.55 + player_position[0] * horizontal_diff;
            var insert_top = 8.3 + (player_position[1] + 1) * vertical_diff;
            
            btn.setAttribute("onclick", "FireArrow('down')");
            btn.style = "background: url('static/interface_elements/easy/move_arrow_red_down.png'); height: 10%; cursor: pointer;"
                + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left + "%;"
            btn.setAttribute('id', 'element' + player_position[0] + ':' + (player_position[1] + 1));
            document.body.appendChild(btn);
            player_elements.push(btn);
        }
        
        
        /* Left Arrow */
        if(player_position[0] > 0)
        {
            btn = document.createElement("button");
            
            // NEEDS TO BE UPDATED
            var insert_left = 2.55 + (player_position[0] - 1) * 5.44;
            var insert_top = 8.3 + player_position[1] * 10.1;
            
            btn.setAttribute("onclick", "FireArrow('left')");
            btn.style = "background: url('static/interface_elements/easy/move_arrow_red_left.png'); height: 10%; cursor: pointer;"
                + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left + "%;"
            btn.setAttribute('id', 'element' + (player_position[0] - 1) + ':' + player_position[1]);
            document.body.appendChild(btn);
            player_elements.push(btn);
        }
        
        
        /* Right Arrow */
        if(player_position[0] < 12)
        {
            btn = document.createElement("button");
            
            // NEEDS TO BE UPDATED
            var insert_left = 2.55 + (player_position[0] + 1) * horizontal_diff;
            var insert_top = 8.3 + player_position[1] * vertical_diff;
            
            btn.setAttribute("onclick", "FireArrow('right')");
            btn.style = "background: url('static/interface_elements/easy/move_arrow_red_right.png'); height: 10%; cursor: pointer;"
                + "width: 8%; background-size: 50% 60%; background-repeat: no-repeat; top: " + insert_top + "%; left: " + insert_left + "%;"
            btn.setAttribute('id', 'element' + (player_position[0] + 1) + ':' + player_position[1]);
            document.body.appendChild(btn);
            player_elements.push(btn);
        }
    }
}