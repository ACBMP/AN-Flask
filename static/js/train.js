import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';



// fake spawn data
let correctSpawn = 2;
let hasGuessed = false;

const scene = new THREE.Scene();

let cameraYaw = 0;
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);

const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById("gameCanvas"),
  antialias: true
});

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

const controls = new PointerLockControls(camera, renderer.domElement);

// lock pointer on click
document.body.addEventListener('click', () => {
  controls.lock();
});

// optional: movement via keyboard
const moveSpeed = 0.2;
const keys = {};
document.addEventListener('keydown', e => keys[e.code] = true);
document.addEventListener('keyup', e => keys[e.code] = false);


function handleMovement() {
  // only vertical movement (Y-axis)
  if (keys['Space']) controls.getObject().position.y += moveSpeed;  // up
  if (keys['ShiftLeft']) controls.getObject().position.y -= moveSpeed;  // down
}

document.addEventListener('mousemove', (event) => {
  cameraYaw = camera.rotation.y;
});

// lighting
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(10, 10, 10);
scene.add(light);

const ambient = new THREE.AmbientLight(0x888888);
scene.add(ambient);

// load OBJ
const loader = new OBJLoader();
function loadMap(name = "siena") {
  loader.load('static/maps/siena.obj', (object) => {
    object.scale.set(1, 1, 1);
    object.rotation.x = -Math.PI / 2; // optional, if your OBJ is Z-up
    scene.add(object);
  }, undefined, (error) => {
    console.error("Error loading OBJ:", error);
  });
  return  [
      {id: 1, x: 10, y: 20, mapX: 10, mapY: 20},
      {id: 2, x: 20, y: 10, mapX: 20, mapY: 10}
  ]
}

let spawnPoints = loadMap();

// --------------------
// minimap
// --------------------
const minimap = document.getElementById("minimap");
const ctx = minimap.getContext("2d");

function worldToMap(x, z, scale = 2) {
  return {
    x: minimap.width / 2 + x * scale,
    y: minimap.height / 2 + z * scale
  };
}

function drawMinimap(scenario) {
  ctx.clearRect(0, 0, minimap.width, minimap.height);

  const p = scenario.player;
  const playerMap = worldToMap(p.x, p.z);

  // -------------------
  // PLAYER (rotating arrow)
  // -------------------
  ctx.save();
  ctx.translate(playerMap.x, playerMap.y);
  ctx.rotate(-cameraYaw);

  ctx.fillStyle = "cyan";
  ctx.beginPath();
  ctx.moveTo(0, -10);
  ctx.lineTo(6, 8);
  ctx.lineTo(-6, 8);
  ctx.closePath();
  ctx.fill();

  ctx.restore();

  // -------------------
  // TEAMMATE (silhouette)
  // -------------------
  const t = worldToMap(scenario.teammate.x, scenario.teammate.z);
  ctx.fillStyle = "white";
  ctx.font = "16px Arial";
  ctx.fillText("🧑", t.x, t.y);

  // -------------------
  // VIP (star)
  // -------------------
  const v = worldToMap(scenario.vip.x, scenario.vip.z);
  ctx.fillText("⭐", v.x, v.y);

  // -------------------
  // SPAWN POINTS
  // -------------------
  spawnPoints.forEach(sp => {
    const m = worldToMap(sp.mapX, sp.mapY);

    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(m.x, m.y, 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "black";
    ctx.fillText(sp.id, m.x + 6, m.y);
  });
}

function addMarker(x, y, z, color) {
  const geo = new THREE.SphereGeometry(0.3);
  const mat = new THREE.MeshBasicMaterial({ color });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  scene.add(mesh);
}

function newRound(scenario) {
  hasGuessed = false;
  correctSpawn = spawnPoints[Math.floor(Math.random() * spawnPoints.length)].id;
  drawMinimap(scenario);
}

setTimeout(newRound, 2000);

function generateScenario() {
  return {
    player: { x: 10, y: 0, z: 20 },
    teammate: { x: -5, y: 0, z: 15 },
    vip: { x: 3, y: 0, z: 8 },
    correctSpawn: null, // computed later
  };
}

let scenario = generateScenario();

addMarker(scenario.teammate.x, 0, scenario.teammate.z, 0xffffff);
addMarker(scenario.vip.x, 0, scenario.vip.z, 0xffff00);

spawnPoints.forEach(sp => {
  addMarker(sp.x, 0, sp.y, 0x888888);
});

// animation loop
function animate() {
  requestAnimationFrame(animate);
  handleMovement();
  drawMinimap(scenario);
  renderer.render(scene, camera);
}

animate();

// --------------------
// guessing logic
// --------------------
minimap.addEventListener("click", (e) => {
  const rect = minimap.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const clicked = spawnPoints.find(p =>
    Math.hypot(p.mapX - x, p.mapY - y) < 10
  );

  if (clicked && !hasGuessed) {
    hasGuessed = true;

    // drawMinimap(scenario, clicked.id, correctSpawn);

    if (clicked.id === correctSpawn) {
      console.log("Correct!");
    } else {
      console.log("Wrong! Correct was:", correctSpawn);
    }
  }
});


// Place the player at the scenario start
controls.getObject().position.set(
  scenario.player.x,
  scenario.player.y + 2,  // eye height above ground
  scenario.player.z
);
