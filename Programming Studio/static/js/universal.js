/* ------------------------------------------------------------------------- */
/* Lair Crushers 2: The Wumpus Strikes Back                                  */
/* Developers:                                                               */
/*     - Aaron Ayrault                                                       */
/*     - Andrew Kirfman                                                      */
/*     - Cheng Chen                                                          */
/*     - Cuong Do                                                            */
/*                                                                           */
/* File: ./static/js/pages/universal.js                           			 */
/* ------------------------------------------------------------------------- */

function Preload() 
{
	for (var i=0; i<Preload.arguments.length; i++) 
	{
	    var new_image = document.createElement('img')
	    new_image.src = Preload.arguments[i];
	    new_image.setAttribute('style', 'height: 0%; width: 0%; top: 0%; left: 0%; opacity: 0.0;')
	    document.body.appendChild(new_image);
	}
}