import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';


const minR = [30, 4, 30]
const smallR = [40, 5, 40]
const largeR = [60, 15, 60]
const maxR = [90, 100, 90]
const w = [0.2, 0.2, 0.5]

function indexOfMax(arr) {
    if (arr.length === 0) {
        return -1;
    }

    var max = arr[0];
    var maxIndex = 0;

    for (var i = 1; i < arr.length; i++) {
        if (arr[i] > max) {
            maxIndex = i;
            max = arr[i];
        }
    }

    return maxIndex;
}

            function calculateScore(cx, cy, screenX, screenY, r2, r3, r1, r4, w) {
                const dx = cx - screenX;
                const dy = cy - screenY;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist > r2 && dist < r3) {
                    // Case 2: valid spawn point
                    return 1;
                } else if (dist >= r1 && dist <= r2) {
                    // Case 1: linear increase from 0 to 1
                    return (dist - r1) / (r2 - r1);
                } else if (dist >= r3 && dist <= r4) {
                    // Case 3: linear decrease from 1 to w
                    return 1 - ((dist - r3) / (r4 - r3)) * (1 - w);
                } else if (dist < r1) {
                    return 0;
                } else {
                    // Outside all ranges
                    return w;
                }
                return score
            }


function getCorrectSpawn(spawnPoints, pursuerPoints, targetPoints) {
    let scores = [];

    for (let [idx, sp] of spawnPoints.entries()) {
        let score = 1;

        pursuerPoints.forEach(p => {
            score *= calculateScore(p.x, p.z, sp.x, sp.y, smallR[0], largeR[0], minR[0], maxR[0], w[0]);
        });
        targetPoints.forEach(p => {
            score *= calculateScore(p.x, p.z, sp.x, sp.y, smallR[2], largeR[2], minR[2], maxR[2], w[2]);
        });
        scores.push(score)
    }
    console.log(pursuerPoints);
    console.log(scores);
    return indexOfMax(scores) + 1;
}


let hasGuessed = false;

const scene = new THREE.Scene();

let cameraYaw = 0;
const camera = new THREE.PerspectiveCamera(
  75,
  16 / 9,
  0.1,
  1000
);

const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById("gameCanvas"),
  antialias: true
});

console.log(window);
renderer.setSize(1140, Math.round(1140 * 9 / 16));
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
    cameraYaw = controls.getObject().rotation.y;
});

// lighting
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(10, 10, 10);
scene.add(light);

const ambient = new THREE.AmbientLight(0x888888);
scene.add(ambient);


// load OBJ
const loader = new OBJLoader();
async function loadMap(name = "siena") {
    // Load spawn points
    let spawns = [];
    try {
        const response = await fetch(`https://api.assassins.network/maps/spawns/${name}`);
        if (!response.ok) throw new Error(`Failed to fetch spawns: ${response.status}`);
        const data = await response.json();
        spawns = data.spawns;
        console.log("Loaded spawns:", spawns);
    } catch (err) {
        console.error("Error loading spawns:", err);
        return [];
    }

    // Load OBJ file
    await new Promise((resolve, reject) => {
        loader.load(
            `static/maps/${name}.obj`,
            (obj) => {
                obj.scale.set(1, 1, 1);
                obj.rotation.x = -Math.PI / 2; // adjust if needed
                obj.rotation.z = Math.PI / 2;
                scene.add(obj);
                resolve();
            },
            undefined,
            (err) => {
                console.error("Error loading OBJ:", err);
                reject(err);
            }
        );
    });

    return spawns;
}

let spawnPoints = await loadMap();
console.log(spawnPoints);

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
    const m = worldToMap(sp.x, sp.y);


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
    }  else if (shape === "arrowDown") {
        // Cone pointing down
        const geo = new THREE.ConeGeometry(size * 0.5, size, 16);
        const mat = new THREE.MeshBasicMaterial({ color });
        mesh = new THREE.Mesh(geo, mat);
        mesh.rotation.x = Math.PI; // flip to point down
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
//
function getBounds(spawnPoints) {
  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;

  spawnPoints.forEach(sp => {
    if (sp.x < minX) minX = sp.x;
    if (sp.x > maxX) maxX = sp.x;
    if (sp.y < minY) minY = sp.y;
    if (sp.y > maxY) maxY = sp.y;
  });

  return { minX, maxX, minY, maxY };
}

function randomInRange(min, max) {
  return Math.random() * (min - max) + max;
}

function generateScenario() {
  const bounds = getBounds(spawnPoints);

  let s = {
    player: {
      x: randomInRange(bounds.minX, bounds.maxX),
      y: 0,
      z: randomInRange(bounds.minY, bounds.maxY)
    },
    teammate: {
      x: randomInRange(bounds.minX, bounds.maxX),
      y: 0,
      z: randomInRange(bounds.minY, bounds.maxY)
    },
    vip: {
      x: randomInRange(bounds.minX, bounds.maxX),
      y: 0,
      z: randomInRange(bounds.minY, bounds.maxY)
    },
    selectedSpawn: null,
  };

  s.correctSpawn = getCorrectSpawn(spawnPoints, [s.player, s.teammate], [s.vip]);
  return s;
}

let scenario = generateScenario();

addMarker3D(scenario.teammate.x, 5, scenario.teammate.z, 0x0000ff);
addMarker3D(scenario.teammate.x, 15, scenario.teammate.z, 0x0000ff, 1, "arrowDown");
addMarker3D(scenario.vip.x, 5, scenario.vip.z, 0xffff00, 0.5, "star");
addMarker3D(scenario.vip.x, 15, scenario.vip.z, 0xffff00, 1, "arrowDown");

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
    Math.hypot(p.x - worldClick.x, p.y - worldClick.z) < 8
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

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let hoveredSpawn = null;
let hoverArrow = null;

// Convert screen coordinates to normalized device coordinates
function updateMouse(event) {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
}

// Store meshes for spawns
const spawnMeshes = spawnPoints.map(sp => {
    const mesh = addNumberedMarker(sp.x, 5, sp.y, sp.id, 0x888888);
    return { id: sp.id, mesh, position: sp };
});

function onMouseMove(event) {
    updateMouse(event);

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(spawnMeshes.map(s => s.mesh));

    if (intersects.length > 0) {
        const intersected = spawnMeshes.find(s => s.mesh === intersects[0].object);

        if (!hoveredSpawn || hoveredSpawn.id !== intersected.id) {
            // Restore previous
            if (hoveredSpawn) {
                hoveredSpawn.mesh.material.color.set(0x888888);
                if (hoverArrow) scene.remove(hoverArrow);
            }

            // Highlight new
            hoveredSpawn = intersected;
            hoveredSpawn.mesh.material.color.set(0xffffff);
            hoverArrow = addMarker3D(
                hoveredSpawn.position.x,
                7, // slightly above
                hoveredSpawn.position.y,
                0xffffff,
                0.5,
                "arrowDown"
            );
        }
    } else if (hoveredSpawn) {
        // Remove highlight if no longer hovering
        hoveredSpawn.mesh.material.color.set(0x888888);
        if (hoverArrow) scene.remove(hoverArrow);
        hoveredSpawn = null;
        hoverArrow = null;
    }
}

window.addEventListener("mousemove", onMouseMove);

// Place the player at the scenario start
controls.getObject().position.set(
  scenario.player.x,
  scenario.player.y + 2,  // eye height above ground
  scenario.player.z
);
scene.add(controls.getObject());

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
