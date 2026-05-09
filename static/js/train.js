import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
const root = document.getElementById("trainingRoot");

const $ = (id) => root.querySelector(id);

const state = new Proxy({
    map: null,
    bandsEnabled: false
}, {
    set(target, key, value) {
        target[key] = value;
        updateUI(key, value);
        return true;
    }
});

let stats = {
    total: 0,
    correct: 0,
    streak: 0,
    maxStreak: 0,
    distanceTotal: 0,
    distanceSum: 0
};
const guessDistanceToggle = $("#guessDistance");
let guessDistanceMode = guessDistanceToggle.checked;

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
    if (guessDistanceMode) {
        const avg = stats.distanceTotal === 0
            ? 0
            : (stats.distanceSum / stats.distanceTotal).toFixed(2);

        $("#stats").innerText =
            `Total: ${stats.distanceTotal} | Avg Distance: ${avg}`;
        return;
    }

    const percent = stats.total === 0
        ? 0
        : ((stats.correct / stats.total) * 100).toFixed(1);

    $("#stats").innerText =
        `Total: ${stats.total} | Correct: ${stats.correct} | ${percent}% | Streak: ${stats.streak} | Max Streak: ${stats.maxStreak}`;
}

loadStats();
updateStatsUI();

guessDistanceToggle.addEventListener("change", () => {
    guessDistanceMode = guessDistanceToggle.checked;
    updateStatsUI();
});

const minR = [30, 4, 30]
const smallR = [40, 5, 40]
const largeR = [60, 15, 60]
const maxR = [90, 100, 90]
const w = [0.2, 0.2, 0.5]
const baseSpawnColor = 0xffffff;
const bandAlpha = 0.1;

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
                    console.log(dist);
                    console.log(r1);
                    console.log("too close");
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
        console.log(idx);

        pursuerPoints.forEach(p => {
            score *= calculateScore(p.x, p.z, sp.x, sp.y, smallR[0], largeR[0], minR[0], maxR[0], w[0]);
        });
        targetPoints.forEach(p => {
            score *= calculateScore(p.x, p.z, sp.x, sp.y, smallR[2], largeR[2], minR[2], maxR[2], w[2]);
        });
        scores.push(score)
        console.log(score);
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
  canvas: $("#gameCanvas"),
  antialias: true
});

const horizontalPadding = 300;
const verticalPadding = 50;

const rootHeight = root.clientHeight;

function resizeCanvas() {
    let gameWidth = window.innerWidth - 2 * horizontalPadding;
    let gameHeight = rootHeight - verticalPadding;

    renderer.setSize(gameWidth, gameHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    camera.aspect = gameWidth / gameHeight;
    camera.updateProjectionMatrix();
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();

const controls = new PointerLockControls(camera, renderer.domElement);

const moveSpeed = 0.2;
const keys = {};
document.addEventListener('keydown', e => {
    if (['Space', 'ShiftLeft', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
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
const light = new THREE.DirectionalLight(baseSpawnColor, 2);
light.position.set(75, 30, 75);
scene.add(light);

const ambient = new THREE.AmbientLight(0x888888);
scene.add(ambient);

const loadingOverlay = $("#loadingOverlay");
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

const mapSelect = $("#mapSelect");
const teammateCountSelect = $("#teammateCount");
const vipCountSelect = $("#vipCount");
const cheatToggle = $("#bandsToggle");
let cheatEnabled = cheatToggle.checked;

cheatToggle.addEventListener("change", () => {
    cheatEnabled = !cheatEnabled;
    drawMinimap(scenario, hoverSpawnId);
});

function getSettings() {
  return {
    teammateCount: parseInt(teammateCountSelect.value, 0),
    vipCount: parseInt(vipCountSelect.value, 0)
  };
}

// const maps = await loadMapList();
// since not all maps are ready let's just hardcode these for now
const maps = ["Siena"];
maps.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    mapSelect.appendChild(opt);
});

// load OBJ
const loader = new OBJLoader();
async function loadMap(name) {
    loadingOverlay.style.display = "flex";
    // Load spawn points
    let spawns = [];
    try {
        const response = await fetch(`https://api.assassins.network/maps/spawns/${name}`);
        if (!response.ok) throw new Error(`Failed to fetch spawns: ${response.status}`);
        const data = await response.json();
        spawns = data.spawns.map(sp => ({id: sp.id, x: sp.y, y: sp.x}));
    } catch (err) {
        console.error("Error loading spawns:", err);
        return [[], []];
    }

    // load routes
    let routes = [];
    try {
        const response = await fetch(`https://api.assassins.network/maps/routes/${name}`);
        if (!response.ok) throw new Error(`Failed to fetch checkpoints: ${response.status}`);
        const data = await response.json();
        // the api needs to be adjusted when we have time
        routes = Object.values(data.routes)
            .flat()
            .map(([y, x]) => ({ x, y }));
    } catch (err) {
        console.error("Error loading routes:", err);
        return [spawns, []];
    }

    // Load OBJ file
    await new Promise((resolve, reject) => {
        loader.load(
            `static/maps/siena.obj`,
            // `static/maps/${name}.obj`,
            (obj) => {
                obj.traverse((child) => {
    if (child.isMesh) {
        // Optional: recompute normals for shading
        // child.geometry.computeVertexNormals();

        // Assign material
        // child.material = new THREE.MeshStandardMaterial({
        //     color: 0x222222, // or 0x888888 for gray
        //     side: THREE.DoubleSide
        // });
    // const edges = new THREE.EdgesGeometry(child.geometry);
    // const line = new THREE.LineSegments(
    //     edges,
    //     new THREE.LineBasicMaterial({ color: baseSpawnColor })
    // );
    // child.add(line);
}
});
                obj.scale.set(1., 1., 1.);
                // obj.rotation.x = -Math.PI / 2; // adjust if needed
                // obj.rotation.y = Math.PI / 2
                // obj.rotation.z = 0.5 * Math.PI;
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

    return [spawns, routes];
}

// --------------------
// minimap
// --------------------
const minimap = $("#minimap");
const ctx = minimap.getContext("2d");
const minimapScale = 2;

function worldToMap(x, z) {
  return {
    x: minimap.width / 2 + x * minimapScale,
    y: minimap.height / 2 + z * minimapScale
  };
}

function mapToWorld(mx, my) {
  return {
    x: (mx - minimap.width / 2) / minimapScale,
    z: (my - minimap.height / 2) / minimapScale
  };
}

function drawMinimapAxes() {
    ctx.strokeStyle = "white";
    ctx.fillStyle = "white";
    ctx.lineWidth = 1;
    const tickSize = 5;
    const tickStep = 50; // pixels per tick

    // --- X-axis (bottom) ---
    ctx.beginPath();
    ctx.moveTo(0, minimap.height - 1);
    ctx.lineTo(minimap.width, minimap.height - 1);
    ctx.stroke();

    for (let i = 0; i <= minimap.width; i += tickStep) {
        ctx.beginPath();
        ctx.moveTo(i, minimap.height - 1);
        ctx.lineTo(i, minimap.height - 1 - tickSize);
        ctx.stroke();
        ctx.fillText((i - minimap.width / 2) / 2, i, minimap.height - 1 - 10); // label in world units (scale 2)
    }

    // --- Z-axis (right) ---
    ctx.beginPath();
    ctx.moveTo(minimap.width - 1, 0);
    ctx.lineTo(minimap.width - 1, minimap.height);
    ctx.stroke();

    for (let j = 0; j <= minimap.height; j += tickStep) {
        ctx.beginPath();
        ctx.moveTo(minimap.width - 1, j);
        ctx.lineTo(minimap.width - 1 - tickSize, j);
        ctx.stroke();
        ctx.fillText((minimap.height / 2 - j) / 2, minimap.width - 1 - 12, j + 4); // label in world units
    }
}

function drawMinimap(scenario, hoveredId = null) {
  ctx.clearRect(0, 0, minimap.width, minimap.height);

        // -------------------
    // AXES
    // -------------------
    drawMinimapAxes();

  const p = scenario.player;
  const playerMap = worldToMap(p.x, p.z);

  // -------------------
  // SPAWN POINTS
  // -------------------
  if (!guessDistanceMode) {
  spawnPoints.slice().reverse().forEach(sp => {
      let color = "white";
      if (sp.id === hoveredId) {
          color = "magenta";
      }
      drawPointMinimap(scenario, ctx, sp, color);
  });
  }

    if (cheatEnabled) {

        // Helper function to draw bands around a world position
        function drawBands(worldX, worldZ, rIndex) {
            const mapPos = worldToMap(worldX, worldZ);

            // Blue: minR → smallR
            ctx.beginPath();
            ctx.arc(mapPos.x, mapPos.y, minimapScale * smallR[rIndex], 0, 2 * Math.PI);
            ctx.arc(mapPos.x, mapPos.y, minimapScale * minR[rIndex], 0, 2 * Math.PI, true);
            ctx.fillStyle = `rgba(0, 0, 255, ${bandAlpha})`;
            ctx.fill();

            // Green: smallR → largeR
            ctx.beginPath();
            ctx.arc(mapPos.x, mapPos.y, minimapScale * largeR[rIndex], 0, 2 * Math.PI);
            ctx.arc(mapPos.x, mapPos.y, minimapScale * smallR[rIndex], 0, 2 * Math.PI, true);
            ctx.fillStyle = `rgba(0, 255, 0, ${bandAlpha})`;
            ctx.fill();

            // Red: largeR → maxR
            ctx.beginPath();
            ctx.arc(mapPos.x, mapPos.y, minimapScale * maxR[rIndex], 0, 2 * Math.PI);
            ctx.arc(mapPos.x, mapPos.y, minimapScale * largeR[rIndex], 0, 2 * Math.PI, true);
            ctx.fillStyle = `rgba(255, 0, 0, ${bandAlpha})`;
            ctx.fill();
        }

        // Draw bands around player (pursuer)
        drawBands(scenario.player.x, scenario.player.z, 0);

        // Draw bands around teammate if exists (pursuer)
        scenario.teammates.forEach(teammate => drawBands(teammate.x, teammate.z, 0));

        // Draw bands around VIPs (targets)
        scenario.vips.forEach(vip => drawBands(vip.x, vip.z, 2));
    }
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
    scenario.teammates.forEach(teammate => {
  const t = worldToMap(teammate.x, teammate.z);
  ctx.fillStyle = "white";
  ctx.font = "16px Arial";
  ctx.fillText("🧑", t.x, t.y);
  });

  // -------------------
  // VIP (star)
  // -------------------
  scenario.vips.forEach(vip => {
    const v = worldToMap(vip.x, vip.z);
    ctx.fillText("⭐", v.x, v.y);
  });

    // -------------------
// CLICK MARKER (X)
// -------------------
if (scenario.clickPosition) {
    const m = worldToMap(
        scenario.clickPosition.x,
        scenario.clickPosition.z
    );

    ctx.strokeStyle = "magenta";
    ctx.lineWidth = 2;

    const size = 8;

    ctx.beginPath();
    ctx.moveTo(m.x - size, m.y - size);
    ctx.lineTo(m.x + size, m.y + size);
    ctx.moveTo(m.x - size, m.y + size);
    ctx.lineTo(m.x + size, m.y - size);
    ctx.stroke();

        const click = worldToMap(scenario.clickPosition.x, scenario.clickPosition.z);
    const correct = spawnPoints[scenario.correctSpawn - 1];
    const correctMap = worldToMap(correct.x, correct.y);

    ctx.strokeStyle = "magenta";
    ctx.setLineDash([5, 5]);

    ctx.beginPath();
    ctx.moveTo(click.x, click.y);
    ctx.lineTo(correctMap.x, correctMap.y);
    ctx.stroke();

    ctx.setLineDash([]);
}
}

let guessLine3D = null; // global

function drawGuessLine3D(guessPos, correctPos) {
    if (guessLine3D) scene.remove(guessLine3D);

    const points = [
        new THREE.Vector3(guessPos.x, 5, guessPos.z),
        new THREE.Vector3(correctPos.x, 5, correctPos.y) // correct spawn uses y as z
    ];

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({ color: 0xff00ff });
    guessLine3D = new THREE.Line(geometry, material);
    scene.add(guessLine3D);
    return guessLine3D;
}

function drawPointMinimap(scenario, ctx, sp, color = "white") {
    const m = worldToMap(sp.x, sp.y);

    ctx.fillStyle = color;
    if (scenario.selectedSpawn) {
        if (sp.id === scenario.correctSpawn) {
          ctx.fillStyle = "green";
        } else if (sp.id === scenario.selectedSpawn && !guessDistanceMode) {
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

function addMarker3D(x, y, z, color = baseSpawnColor, size = 0.5, shape = "sphere") {
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

function addNumberedMarker(x, y, z, num, color = baseSpawnColor, size = 0.5) {
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

function addClickMarkerX(x, y, z, color = 0xff00ff, size = 1) {
    const material = new THREE.LineBasicMaterial({ color });

    const points1 = [
        new THREE.Vector3(-size, 0, -size),
        new THREE.Vector3(size, 0, size)
    ];

    const points2 = [
        new THREE.Vector3(-size, 0, size),
        new THREE.Vector3(size, 0, -size)
    ];

    const geo1 = new THREE.BufferGeometry().setFromPoints(points1);
    const geo2 = new THREE.BufferGeometry().setFromPoints(points2);

    const line1 = new THREE.Line(geo1, material);
    const line2 = new THREE.Line(geo2, material);

    const group = new THREE.Group();
    group.add(line1);
    group.add(line2);

    group.position.set(x, y, z);
    scene.add(group);

    return group;
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
  const settings = getSettings();

  const s = {
    player: {
      x: randomInRange(bounds.minX, bounds.maxX),
      y: 0,
      z: randomInRange(bounds.minY, bounds.maxY)
    },
    teammates: [],
    vips: [],
    selectedSpawn: null,
    clickPosition: null,
  };

    for (let i = 0; i < settings.teammateCount; i++) {
    s.teammates.push({
      x: randomInRange(bounds.minX, bounds.maxX),
      y: 0,
      z: randomInRange(bounds.minY, bounds.maxY)
    });
  }

  for (let i = 0; i < settings.vipCount; i++) {
      let chosenPoint = checkPoints[Math.floor(Math.random() * checkPoints.length)];
    s.vips.push({
      x: chosenPoint.x,
      y: 0,
      z: chosenPoint.y
    });
  }

  const pursuers = [s.player].concat(s.teammates);

  s.correctSpawn = getCorrectSpawn(spawnPoints, pursuers, s.vips);

  return s;
}

let spawnMarkers = [];
let personaMarkers = [];
function populateScene(scenario, spawnPoints) {
  spawnMarkers = [];

  personaMarkers = []
    scenario.teammates.forEach(teammate => {
    personaMarkers.push(addMarker3D(teammate.x, 5, teammate.z, 0x0000ff));
    personaMarkers.push(addMarker3D(teammate.x, 15, teammate.z, 0x0000ff, 1, "arrowDown"));
    });

  scenario.vips.forEach(vip => {
    personaMarkers.push(addMarker3D(vip.x, 5, vip.z, 0xffff00, 0.5, "star"));
    personaMarkers.push(addMarker3D(vip.x, 15, vip.z, 0xffff00, 1, "arrowDown"));
  });

    if (!guessDistanceMode) {
  spawnPoints.forEach(sp => {
    spawnMarkers.push(addNumberedMarker(sp.x, 5, sp.y, sp.id));
  });
    }
}

function restartScenario() {
  personaMarkers.forEach(m => {
      scene.remove(m);
  });
  scenario = generateScenario();
  populateScene(scenario, spawnPoints);
}

teammateCountSelect.addEventListener("change", restartScenario);
vipCountSelect.addEventListener("change", restartScenario);

let [spawnPoints, checkPoints] = await loadMap(mapSelect.value.toLowerCase());
let scenario = generateScenario();
populateScene(scenario, spawnPoints);

mapSelect.addEventListener("change", async () => {
    scene.clear();

    [spawnPoints, checkPoints] = await loadMap(mapSelect.value.toLowerCase());
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

    const basic_mesh = new THREE.MeshBasicMaterial({ color: baseSpawnColor });
    spawnMarkers[scenario.correctSpawn - 1].material = basic_mesh;
    if (guessDistanceMode) {
        if (clickMarkerMesh) {
            scene.remove(clickMarkerMesh);
            clickMarkerMesh = null;
            scene.remove(guessLine3D);
            guessLine3D = null;
        }
    } else if (scenario.selectedSpawn) spawnMarkers[scenario.selectedSpawn - 1].material = basic_mesh;
    personaMarkers.forEach(m => scene.remove(m));
    personaMarkers = [];
    scenario = generateScenario();
    populateScene(scenario, spawnPoints);

    // reset player position
    controls.getObject().position.set(
        scenario.player.x,
        scenario.player.y + 2,
        scenario.player.z
    );
    camera.lookAt(0, 5, 0);

    // reset distance
    $("#distanceResult").innerText = "";

    if (clickMarkerMesh) {
        scene.remove(clickMarkerMesh);
        clickMarkerMesh = null;
    }
}

// --------------------
// guessing logic
// --------------------
function getClosestSpawn(worldX, worldZ, spawnPoints) {
    let closest = null;
    let minDist = Infinity;

    spawnPoints.forEach(sp => {
        const dx = worldX - sp.x;
        const dz = worldZ - sp.y; // spawn uses (x, y)

        const dist = dx * dx + dz * dz; // squared distance (faster)

        if (dist < minDist) {
            minDist = dist;
            closest = sp;
        }
    });

    return closest;
}

minimap.addEventListener("click", (e) => {
  e.stopPropagation();  // Prevent the click from bubbling up
  e.preventDefault();  // prevent focus/locking

const rect = minimap.getBoundingClientRect();
const x = e.clientX - rect.left;
const y = e.clientY - rect.top;
const worldClick = mapToWorld(x, y);

// ----------------------------
// DISTANCE MODE
// ----------------------------
if (guessDistanceMode) {
    const correct = spawnPoints[scenario.correctSpawn - 1];
        scenario.clickPosition = {
        x: worldClick.x,
        z: worldClick.z
    };
    if (hasGuessed) return;
    hasGuessed = true;

    const dx = worldClick.x - correct.x;
    const dz = worldClick.z - correct.y; // note: spawn uses (x, y)
    const dist = Math.sqrt(dx * dx + dz * dz);

    // remove old marker
if (clickMarkerMesh) scene.remove(clickMarkerMesh);

// add new marker at exact click
clickMarkerMesh = addClickMarkerX(
    worldClick.x,
    5,              // height above ground
    worldClick.z,
    0xff00ff,
    1
);
        guessLine3D = drawGuessLine3D({x: worldClick.x, z: worldClick.z}, correct);

// still keep closest spawn if you want stats/debug
scenario.selectedSpawn = getClosestSpawn(worldClick.x, worldClick.z, spawnPoints);

    // stats
    stats.distanceTotal++;
    stats.distanceSum += dist;

    $("#distanceResult").innerText =
        `Distance: ${dist.toFixed(2)}`;

    updateStatsUI();
    drawMinimap(scenario);

    return;
}

// ----------------------------
// NORMAL MODE (unchanged)
// ----------------------------
const clicked = spawnPoints.find(sp =>
        Math.hypot(sp.x - worldClick.x, sp.y - worldClick.z) < 5
    );
if (!clicked || hasGuessed) return;

hasGuessed = true;

scenario.selectedSpawn = clicked.id;
drawMinimap(scenario);

stats.total++;
if (clicked.id === scenario.correctSpawn) {
    stats.correct++;
    stats.streak++;
    if (stats.streak > stats.maxStreak) stats.maxStreak = stats.streak;
} else {
    stats.streak = 0;
}

saveStats();
updateStatsUI();
});

$("#nextBtn").addEventListener("click", () => {
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
let clickMarkerMesh = null;

function onMinimapHover(e) {
    const rect = minimap.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const worldPos = mapToWorld(mx, my);

    // Find the spawn we're hovering over (radius 5 in minimap units)
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
  if (scenario.selectedSpawn && spawnMarkers) {
      let cp = spawnMarkers[scenario.correctSpawn - 1];
      cp.material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
      if (!guessDistanceMode && scenario.correctSpawn != scenario.selectedSpawn) {
          let sp = spawnMarkers[scenario.selectedSpawn - 1];
          sp.material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
      };
  };
  renderer.render(scene, camera);
}

animate();
