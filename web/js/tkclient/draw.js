define(function () {
	var dicewidth = 100;
	var diceheight = 100;
	var dotrad = 6;

	var drawtest = function () {
		var i;
		for (i = 1; i <= 5; i++) {
			drawdice(1 + Math.floor(Math.random()*6), $('#d' + i));
		}
	};

	var drawdice = function (n, canvas) {
		var context = canvas[0].getContext('2d');
		context.lineWidth = 5;
		context.clearRect(0,0,dicewidth,diceheight);
		context.strokeRect(0,0,dicewidth,diceheight);

		context.fillStyle = "#009966";
		switch(n) {
			case 1:
			 draw1(context);
			 break;
			case 2:
			 draw2(context);
			 break;
			case 3:
			 draw2(context);
			 draw1(context);
			 break;
			case 4:
			 draw4(context);
			 break;
			case 5:
			 draw4(context);
			 draw1(context);
			 break;
			case 6:
			 draw4(context);
			 draw2mid(context);
			 break;
		}
	};
	function draw1(context) {
		var dotx;
		var doty;
		context.beginPath();
		dotx = .5*dicewidth;
		doty = .5*diceheight;
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		context.closePath();
		context.fill();
	}

	function draw2(context) {
		var dotx;
		var doty;
		context.beginPath();
		dotx = 3*dotrad;
		doty = 3*dotrad;
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		dotx = dicewidth-3*dotrad;
		doty = diceheight-3*dotrad;
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		context.closePath();
		context.fill();
	}

	function draw4(context) {
		var dotx;
		var doty;
		context.beginPath();
		dotx = 3*dotrad;
		doty = 3*dotrad;
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		dotx = dicewidth-3*dotrad;
		doty = diceheight-3*dotrad;
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		context.closePath();
		context.fill();
		context.beginPath();
		dotx = 3*dotrad;
		doty = diceheight-3*dotrad;  //no change
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		dotx = dicewidth-3*dotrad;
		doty = 3*dotrad;
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		context.closePath();
		context.fill();
	}
	function draw2mid(context) {
		var dotx;
		var doty;
		context.beginPath();
		dotx = 3*dotrad;
		doty = .5*diceheight;
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		dotx = dicewidth-3*dotrad;
		doty = .5*diceheight; //no change
		context.arc(dotx,doty,dotrad,0,Math.PI*2,true);
		context.closePath();
		context.fill();
	}

    return {
        drawtest: drawtest,
        drawdice: drawdice
    }


});

