var Engine = Matter.Engine,
    // Render = Matter.Render,
    // Runner = Matter.Runner,
    World = Matter.World,
    Bodies = Matter.Bodies;
    // Composite = Matter.Composite;

var engine;
var world;
var boxes = [];

var ground;

function setup() 
{
  createCanvas(1536,775);
  engine = Engine.create();
  world = engine.world;
  Engine.run(engine);
  var options = {
    isStatic: true
  }
  ground = Bodies.rectangle(768, height, width, 10, options);
  World.add(world, ground);
}
function mouseDragged()
{
  boxes.push(new Box(mouseX, mouseY,30, 30));
}
function draw() 
{
  background(51);
  for(var i =0; i < boxes.length ; i++)
  {
    boxes[i].show();
  }
  noStroke(255);
  fill(170);
  rectMode(CENTER);
  rect(768, height, width, 10)
}
