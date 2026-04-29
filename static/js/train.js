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

console.log(window);
renderer.setSize(1140, window.innerHeight - 40);
renderer.setPixelRatio(window.devicePixelRatio);

const controls = new PointerLockControls(camera, renderer.domElement);

// lock pointer on click
document.body.addEventListener('click', (e) => {
  // Only lock pointer if the click was NOT on the minimap
  if (!controls.isLocked && e.target !== minimap) {
    controls.lock();
  }
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
      {id: 1, x: 30, y: 20, mapX: 30, mapY: 20},
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

function mapToWorld(mx, my, scale = 2) {
  return {
    x: (mx - minimap.width / 2) / scale,
    z: (my - minimap.height / 2) / scale
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
    if (scenario.selectedSpawn) {
        if (sp.id === scenario.correctSpawn) {
          ctx.fillStyle = "green";
        } else if (sp.id === scenario.selectedSpawn) {
          ctx.fillStyle = "red";
        }
    };

    ctx.beginPath();
    ctx.arc(m.x, m.y, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "black";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(sp.id, m.x, m.y);
  });
}

function addMarker(x, y, z, color) {
  const geo = new THREE.SphereGeometry(0.3);
  const mat = new THREE.MeshBasicMaterial({ color });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  scene.add(mesh);
}

function addMarker3D(x, y, z, color = 0xffffff, size = 0.5, shape = "sphere") {
    let mesh;
    if (shape === "sphere") {
        const geo = new THREE.SphereGeometry(size, 16, 16);
        const mat = new THREE.MeshBasicMaterial({ color });
        mesh = new THREE.Mesh(geo, mat);
    } else if (shape === "star") {
        const geo = new THREE.OctahedronGeometry(size); // simple star-like
        const mat = new THREE.MeshBasicMaterial({ color });
        mesh = new THREE.Mesh(geo, mat);
    }
    mesh.position.set(x, y, z);
    scene.add(mesh);
    return mesh;
}

function addNumberedMarker(x, y, z, num, color = 0x888888, size = 0.5) {
    // 3D marker sphere
    const sphereGeo = new THREE.SphereGeometry(size, 16, 16);
    const sphereMat = new THREE.MeshBasicMaterial({ color });
    const sphere = new THREE.Mesh(sphereGeo, sphereMat);
    sphere.position.set(x, y, z);
    scene.add(sphere);

    // Create canvas for number
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const context = canvas.getContext('2d');
    context.fillStyle = "white";
    context.font = "bold 48px Arial";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(num, canvas.width / 2, canvas.height / 2);

    // Create texture & sprite
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(1, 1, 1);  // adjust size
    sprite.position.set(x, y + size + 0.3, z); // slightly above the sphere
    scene.add(sprite);

    return sphere;
}

// function newRound(scenario) {
//   hasGuessed = false;

//   // Pick one random spawn as the correct one
//   const randomIndex = Math.floor(Math.random() * spawnPoints.length);
//   scenario.correctSpawn = spawnPoints[randomIndex].id;

//   drawMinimap(scenario);
// }

// setTimeout(newRound, 2000);

function generateScenario() {
  return {
    player: { x: 10, y: 0, z: 20 },
    teammate: { x: -5, y: 0, z: 15 },
    vip: { x: 3, y: 0, z: 8 },
    correctSpawn: 1, // computed later
    selectedSpawn: null,
  };
}

let scenario = generateScenario();

addMarker3D(scenario.teammate.x, 5, scenario.teammate.z, 0xffffff);
addMarker3D(scenario.vip.x, 5, scenario.vip.z, 0xffff00, 0.5, "star");

spawnPoints.forEach(sp => {
  addNumberedMarker(sp.x, 5, sp.y, sp.id, 0x888888);
});


// --------------------
// guessing logic
// --------------------
minimap.addEventListener("click", (e) => {
  e.stopPropagation();  // Prevent the click from bubbling up
  e.preventDefault();  // prevent focus/locking

  const rect = minimap.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const worldClick = mapToWorld(x, y);
  const clicked = spawnPoints.find(p =>
    Math.hypot(p.mapX - worldClick.x, p.mapY - worldClick.z) < 8
  );

  if (!clicked || hasGuessed) return;

  hasGuessed = true;

  scenario.selectedSpawn = clicked.id;
  drawMinimap(scenario);

  if (clicked.id === scenario.correctSpawn) {
    console.log("Correct!");
  } else {
    console.log("Wrong! Correct was:", scenario.correctSpawn);
  }
});

// Place the player at the scenario start
controls.getObject().position.set(
  scenario.player.x,
  scenario.player.y + 2,  // eye height above ground
  scenario.player.z
);

// animation loop
function animate() {
  requestAnimationFrame(animate);
  handleMovement();
  drawMinimap(scenario);
  if (scenario.selectedSpawn) {
      let cp = spawnPoints[scenario.correctSpawn - 1];
      addNumberedMarker(cp.x, 5, cp.y, cp.id, 0x00ff00);
      if (scenario.correctSpawn != scenario.selectedSpawn) {
          let sp = spawnPoints[scenario.selectedSpawn - 1];
          addNumberedMarker(sp.x, 5, sp.y, sp.id, 0xff0000);
      };
  };
  renderer.render(scene, camera);
}

animate();
