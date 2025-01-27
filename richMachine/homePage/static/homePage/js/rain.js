// const { path } = require("express/lib/application");

let canvas = document.getElementsByClassName('rain')[0];

let c = canvas.getContext('2d');

function randomNum(max, min) {
	return Math.floor(Math.random() * max) + min;
}

function RainDrops(svgPath) {

	this.x = Math.floor(Math.random() * window.innerWidth) + 1;
	this.y = Math.random() * -500;
	this.endy = randomNum(10, 2);
	this.velocity = randomNum(1.9, 1.2);
	this.opacity = Math.random() * .55;
    this.svg = new Image();
    this.svg.src = svgPath;

	this.draw = function() {
        c.drawImage(this.svg, this.x, this.y, 20, 40); 
    }

	this.update = function() {
		let rainEnd = window.innerHeight;
		if (this.y >= rainEnd) {
			this.y = this.endy - 100;
		} else {
			this.y = this.y + this.velocity;
		}
		this.draw();
	}

}

let rainArray = [];
let svgPath = 'static/homePage/img/dollar.svg';

for (let i = 0; i < 14; i++) {
	rainArray.push(new RainDrops(svgPath));
}

function animateRain() {
	
	canvas.width = window.innerWidth - 100;
	canvas.height = window.innerHeight - 20;
	
	requestAnimationFrame(animateRain);
	c.clearRect(0,0, window.innerWidth, window.innerHeight);

	for (let i = 0; i < rainArray.length; i++) {
		rainArray[i].update();
	}

}

animateRain();


