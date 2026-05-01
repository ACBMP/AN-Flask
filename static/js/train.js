import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

let stats = {
    total: 0,
    correct: 0,
    streak: 0
};

function saveStats() {
    document.cookie = "stats=" + JSON.stringify(stats) + ";path=/";
}

function loadStats() {
    const match = document.cookie.match(/stats=([^;]+)/);
    if (match) {
        stats = JSON.parse(match[1]);
    }
}

function updateStatsUI() {
    const percent = stats.total === 0
        ? 0
        : ((stats.correct / stats.total) * 100).toFixed(1);

    document.getElementById("stats").innerText =
        `Total: ${stats.total} | Correct: ${stats.correct} | ${percent}% | Streak: ${stats.streak}`;
}

loadStats();
updateStatsUI();

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

let gameWidth = 1320;
renderer.setSize(gameWidth, Math.round(gameWidth * 9 / 16));
renderer.setPixelRatio(window.devicePixelRatio);

const controls = new PointerLockControls(camera, renderer.domElement);

// optional: movement via keyboard
const moveSpeed = 0.2;
const keys = {};
document.addEventListener('keydown', e => {
    if (['Space', 'ShiftLeft', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
        // Only prevent if pointer is locked OR mouse is over the canvas
        if (document.activeElement === renderer.domElement || controls.isLocked) {
            e.preventDefault();
        }
    }
    keys[e.code] = true;
});

document.addEventListener('keyup', e => keys[e.code] = false);


function handleMovement() {
  // only vertical movement (Y-axis)
  if (keys['Space']) controls.getObject().position.y += moveSpeed;  // up
  if (keys['ShiftLeft']) controls.getObject().position.y -= moveSpeed;  // down
}

function getCameraYawAngle() {
    // Forward vector in world space
    const forward = new THREE.Vector3(0, 0, -1);
    forward.applyQuaternion(controls.getObject().quaternion); // rotate by camera orientation

    // Compute angle on XZ plane
    const angle = Math.atan2(forward.x, forward.z); // atan2(x, z) gives compass-like heading
    return angle + Math.PI;
}
document.addEventListener('mousemove', (event) => {
    cameraYaw = getCameraYawAngle();
});

// lighting
const light = new THREE.DirectionalLight(0xffffff, 2);
light.position.set(0, 30, 0);
scene.add(light);

const ambient = new THREE.AmbientLight(0x888888);
scene.add(ambient);

const loadingOverlay = document.getElementById('loadingOverlay');
let dots = 0;
const loadingInterval = setInterval(() => {
    if (loadingOverlay.style.display === 'flex') {
        dots = (dots + 1) % 4;
        loadingOverlay.innerText = "Loading map" + ".".repeat(dots);
    } else {
        clearInterval(loadingInterval);
    }
}, 500);

async function loadMapList() {
    try {
        const res = await fetch("https://api.assassins.network/maps/list/Escort");
        const data = await res.json();
        return data.map(m => m.name).sort();
    } catch (e) {
        console.error("Failed to load map list", e);
        return [];
    }
}

const mapSelect = document.getElementById("mapSelect");

const maps = await loadMapList();
maps.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    mapSelect.appendChild(opt);
});

// load OBJ
const loader = new OBJLoader();
async function loadMap(name = "siena") {
    loadingOverlay.style.display = "flex";
    // Load spawn points
    let spawns = [];
    try {
        const response = await fetch(`https://api.assassins.network/maps/spawns/${name}`);
        if (!response.ok) throw new Error(`Failed to fetch spawns: ${response.status}`);
        const data = await response.json();
        spawns = data.spawns;
    } catch (err) {
        console.error("Error loading spawns:", err);
        return [];
    }

    // Load OBJ file
    await new Promise((resolve, reject) => {
        loader.load(
            `static/maps/${name}.obj`,
            (obj) => {
                obj.traverse((child) => {
    if (child.isMesh) {
        // Optional: recompute normals for shading
        child.geometry.computeVertexNormals();

        // Assign material
        child.material = new THREE.MeshStandardMaterial({
            color: 0x888888, // or 0x888888 for gray
            side: THREE.DoubleSide
        });
    const edges = new THREE.EdgesGeometry(child.geometry);
    const line = new THREE.LineSegments(
        edges,
        new THREE.LineBasicMaterial({ color: 0xffffff })
    );
    child.add(line);
}
});
                obj.scale.set(1.2, 1.2, 1.2);
                obj.rotation.x = -Math.PI / 2; // adjust if needed
                // obj.rotation.y = Math.PI / 2
                obj.rotation.z = Math.PI / 2;
                scene.add(obj);
                loadingOverlay.style.display = "none";
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

function drawMinimap(scenario, hoveredId = null) {
  ctx.clearRect(0, 0, minimap.width, minimap.height);

  const p = scenario.player;
  const playerMap = worldToMap(p.x, p.z);

  // -------------------
  // SPAWN POINTS
  // -------------------
  spawnPoints.slice().reverse().forEach(sp => {
      let color = "white";
      if (sp.id === hoveredId) {
          color = "magenta";
      }
      drawPointMinimap(scenario, ctx, sp, color);
  });

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
}

function drawPointMinimap(scenario, ctx, sp, color = "white") {
    const m = worldToMap(sp.x, sp.y);

    ctx.fillStyle = color;
    if (scenario.selectedSpawn) {
        if (sp.id === scenario.correctSpawn) {
          ctx.fillStyle = "green";
        } else if (sp.id === scenario.selectedSpawn) {
          ctx.fillStyle = "red";
        }
    };

    ctx.beginPath();
    ctx.arc(m.x, m.y, 10, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "black";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(sp.id, m.x, m.y);
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

function addNumberedMarker(x, y, z, num, color = 0xaaaaaa, size = 0.5) {
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

let spawnMarkers = [];
function populateScene(scenario, spawnPoints) {
    addMarker3D(scenario.teammate.x, 5, scenario.teammate.z, 0x0000ff);
    addMarker3D(scenario.teammate.x, 15, scenario.teammate.z, 0x0000ff, 1, "arrowDown");
    addMarker3D(scenario.vip.x, 5, scenario.vip.z, 0xffff00, 0.5, "star");
    addMarker3D(scenario.vip.x, 15, scenario.vip.z, 0xffff00, 1, "arrowDown");

    spawnPoints.forEach(sp => {
        spawnMarkers.push(addNumberedMarker(sp.x, 5, sp.y, sp.id));
    });
}


// let spawnPoints = await loadMap(mapSelect.value.toLowerCase());
let spawnPoints = await loadMap("siena");
let scenario = generateScenario();
populateScene(scenario, spawnPoints);

mapSelect.addEventListener("change", async () => {
    scene.clear();

    spawnPoints = await loadMap(mapSelect.value.toLowerCase());
    scenario = generateScenario();

    populateScene(scenario, spawnPoints);
});

function nextRound() {
    hasGuessed = false;
    hoverSpawnId = null;

    // remove hover meshes
    if (hoverArrowMesh) scene.remove(hoverArrowMesh);
    if (hoverMarkerMesh) scene.remove(hoverMarkerMesh);
    hoverArrowMesh = null;
    hoverMarkerMesh = null;

    const basic_mesh = new THREE.MeshBasicMaterial({ color: 0xaaaaaa });
    spawnMarkers[scenario.correctSpawn - 1].material = basic_mesh;
    spawnMarkers[scenario.selectedSpawn - 1].material = basic_mesh;
    scenario = generateScenario();

    // reset player position
    controls.getObject().position.set(
        scenario.player.x,
        scenario.player.y + 2,
        scenario.player.z
    );
    camera.lookAt(0, 5, 0);
}

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

  stats.total++;
  if (clicked.id === scenario.correctSpawn) {
    console.log("Correct!");
    stats.correct++;
    stats.streak++;
  } else {
    console.log("Wrong! Correct was:", scenario.correctSpawn);
    stats.streak = 0;
  }
  saveStats();
  updateStatsUI();
});

document.getElementById("nextBtn").addEventListener("click", () => {
    nextRound();
});

// lock pointer on click if in gameCanvas
document.body.addEventListener('click', (e) => {
  if (!controls.isLocked && e.target === gameCanvas) {
    controls.lock();
  }
});


const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let hoverSpawnId = null;
let hoverArrowMesh = null;
let hoverMarkerMesh = null;

function onMinimapHover(e) {
    const rect = minimap.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const worldPos = mapToWorld(mx, my);

    // Find the spawn we're hovering over (radius 4 in minimap units)
    const hovered = spawnPoints.find(sp =>
        Math.hypot(sp.x - worldPos.x, sp.y - worldPos.z) < 5
    );

    if (hovered) {
        if (hoverSpawnId !== hovered.id) {
            // Restore previous spawn
            if (hoverSpawnId !== null) {
                const prev = spawnPoints.find(sp => sp.id === hoverSpawnId);
                if (prev && hoverArrowMesh) scene.remove(hoverArrowMesh);
                if (prev && hoverMarkerMesh) scene.remove(hoverMarkerMesh);
            }

            // Set new hover
            hoverSpawnId = hovered.id;

            // Add arrow above spawn
            hoverArrowMesh = addMarker3D(
                hovered.x,
                7,  // adjust height above
                hovered.y,
                0xff00ff,
                0.5,
                "arrowDown"
            );

            // Change marker color (optional)
            // You could store mesh references for each spawn if you want to recolor
            hoverMarkerMesh = addMarker3D(
                hovered.x,
                5,
                hovered.y,
                0xff00ff,
                0.6,
                "sphere"
            );
        }
    } else {
        // Not hovering any spawn
        if (hoverSpawnId !== null) {
            if (hoverArrowMesh) scene.remove(hoverArrowMesh);
            if (hoverMarkerMesh) scene.remove(hoverMarkerMesh);
            hoverSpawnId = null;
            hoverArrowMesh = null;
            hoverMarkerMesh = null;
        }
    }

    // Redraw minimap so the hover color can be applied
    drawMinimap(scenario, hoverSpawnId);
}

// Listen for mouse move over the minimap
minimap.addEventListener("mousemove", onMinimapHover);

// Optional: remove arrow if the mouse leaves the minimap
minimap.addEventListener("mouseleave", () => {
    if (hoverArrowMesh) scene.remove(hoverArrowMesh);
    if (hoverMarkerMesh) scene.remove(hoverMarkerMesh);
    hoverSpawnId = null;
    hoverArrowMesh = null;
    hoverMarkerMesh = null;
    drawMinimap(scenario, hoverSpawnId);
});

// Place the player at the scenario start
controls.getObject().position.set(
  scenario.player.x,
  scenario.player.y + 2,  // eye height above ground
  scenario.player.z
);
camera.lookAt(0, 5, 0);
scene.add(controls.getObject());

// animation loop
function animate() {
  requestAnimationFrame(animate);
  handleMovement();
  drawMinimap(scenario, hoverSpawnId);
  if (scenario.selectedSpawn) {
      let cp = spawnMarkers[scenario.correctSpawn - 1];
      cp.material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
      if (scenario.correctSpawn != scenario.selectedSpawn) {
          let sp = spawnMarkers[scenario.selectedSpawn - 1];
          sp.material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
      };
  };
  renderer.render(scene, camera);
}

animate();
