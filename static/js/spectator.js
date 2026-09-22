(function () {
  "use strict";

  var root = document.getElementById("spectator-root");
  if (!root) return;

  var WORLD_MIN = -65;
  var WORLD_MAX = 65;
  var DEATH_MARK_SECONDS = 6;
  var ACTIVITY_LOG_MAX = 30;

  var mode = root.dataset.mode;

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  function pct(coord) {
    var t = (coord - WORLD_MIN) / (WORLD_MAX - WORLD_MIN);
    return clamp(t, 0, 1) * 100;
  }

  // character_id -> {name, icon}, ported from ACB-2.0-Patch's diagnostics.cpp
  // (kCharacterNames). `icon` is the exact filename under static/char_svg/
  // (an existing site asset) -- given explicitly rather than derived by
  // lowercasing/underscoring the name, since "Dama Rossa"'s real file has a
  // space, not an underscore (the PoC's own slug-guessing approach silently
  // 404s on that one). An id missing here (unreleased/unmapped character, or
  // player_stats not available yet) just means no class name/icon is shown --
  // never a broken render.
  var CHARACTERS = {
    2: { name: "Harlequin", icon: "harlequin.svg" },
    5: { name: "Doctor", icon: "doctor.svg" },
    7: { name: "Priest", icon: "priest.svg" },
    8: { name: "Nobleman", icon: "nobleman.svg" },
    10: { name: "Prowler", icon: "prowler.svg" },
    14: { name: "Courtesan", icon: "courtesan.svg" },
    15: { name: "Barber", icon: "barber.svg" },
    17: { name: "Executioner", icon: "executioner.svg" },
    18: { name: "Engineer", icon: "engineer.svg" },
    20: { name: "Captain", icon: "captain.svg" },
    21: { name: "Officer", icon: "officer.svg" },
    22: { name: "Hellequin", icon: "hellequin.svg" },
    23: { name: "Footpad", icon: "footpad.svg" },
    24: { name: "Blacksmith", icon: "blacksmith.svg" },
    25: { name: "Smuggler", icon: "smuggler.svg" },
    26: { name: "Mercenary", icon: "mercenary.svg" },
    27: { name: "Thief", icon: "thief.svg" },
    28: { name: "Pariah", icon: "pariah.svg" },
    31: { name: "Knight", icon: "knight.svg" },
    32: { name: "Dama Rossa", icon: "dama rossa.svg" },
    34: { name: "Marquis", icon: "marquis.svg" }
  };

  function characterNameFor(characterId) {
    var c = CHARACTERS[characterId];
    return c ? c.name : null;
  }

  function characterIconUrl(characterId) {
    var c = CHARACTERS[characterId];
    return c ? "/static/char_svg/" + encodeURIComponent(c.icon) : null;
  }

  // Per-map background + coordinate calibration, ported from the PoC's
  // map.html (MAP_DEFS): world-space corners (game's ground-plane X/Y) and
  // the matching pixel corners on that map's background jpg. Only maps with
  // a background image shipped in static/maps/ get an entry here -- the rest
  // (Alhambra, Mont-Saint-Michel, Pienza) resolve a display name server-side
  // but have no calibrated key, so they always fall back to the grid.
  var MAP_DEFS = {
    forli: {
      label: "Forlì", image: "forli.jpg", imgW: 658, imgH: 630,
      world: { tl: [-56.6, 58.5], br: [56.6, -49.5] }, pixel: { tl: [4, 18], br: [653, 621] }
    },
    rome: {
      label: "Rome", image: "rome.jpg", imgW: 540, imgH: 540,
      world: { tl: [-62, 66], br: [52, -62.3] }, pixel: { tl: [32.5, 8.5], br: [493, 530] }
    },
    san_donato: {
      label: "San Donato", image: "san_donato.jpg", imgW: 658, imgH: 651,
      world: { tl: [-50.5, 55], br: [55.5, -52] }, pixel: { tl: [88, 62], br: [624, 599] }
    },
    siena: {
      label: "Siena", image: "siena.jpg", imgW: 621, imgH: 397,
      world: { tl: [-55, 46], br: [58, -25] }, pixel: { tl: [8, 7], br: [610, 386.25] }
    },
    venice: {
      label: "Venice", image: "venice.jpg", imgW: 453, imgH: 656,
      world: { tl: [5.1, 27.9], br: [84, -92] }, pixel: { tl: [28, 45], br: [445, 655] }
    },
    castel_gandolfo: {
      label: "Castel Gandolfo", image: "castel_gandolfo.jpg", imgW: 623, imgH: 538,
      world: { tl: [-51, 41], br: [51, -45] }, pixel: { tl: [2, 9], br: [621, 531] }
    },
    florence: {
      label: "Florence", image: "florence.jpg", imgW: 623, imgH: 544,
      world: { tl: [-51, 44], br: [51, -43] }, pixel: { tl: [76, 57], br: [603, 507] }
    },
    monteriggioni: {
      label: "Monteriggioni", image: "monteriggioni.jpg", imgW: 624, imgH: 624,
      world: { tl: [-66.5, 66.5], br: [66.5, -42.5] }, pixel: { tl: [41, 130], br: [573, 567] }
    }
  };

  var mapLayoutCache = {};
  function mapLayoutFor(key) {
    var def = MAP_DEFS[key];
    if (!def) return null;
    if (mapLayoutCache[key]) return mapLayoutCache[key];
    var sx = (def.pixel.br[0] - def.pixel.tl[0]) / (def.world.br[0] - def.world.tl[0]);
    var sy = (def.pixel.br[1] - def.pixel.tl[1]) / (def.world.br[1] - def.world.tl[1]);
    var ox = def.pixel.tl[0] - sx * def.world.tl[0];
    var oy = def.pixel.tl[1] - sy * def.world.tl[1];
    var layout = {
      def: def,
      toXPct: function (wx) {
        return clamp(((sx * wx + ox) / def.imgW) * 100, 0, 100);
      },
      toYPct: function (wy) {
        return clamp(((sy * wy + oy) / def.imgH) * 100, 0, 100);
      }
    };
    mapLayoutCache[key] = layout;
    return layout;
  }

  // Manual background selection, mirroring the PoC's "Background" dropdown --
  // brought back specifically for the case where the ingest payload carries
  // no recognizable map (recording.map_key empty), since there's then no way
  // to auto-pick a calibrated background. When the server DID resolve a
  // known map_key, that's used directly and the picker stays hidden.
  var selectedMapKey = root.dataset.mapKey && MAP_DEFS[root.dataset.mapKey] ? root.dataset.mapKey : "";
  var mapKnownFromServer = !!selectedMapKey;

  function applyMinimapBackground() {
    var minimap = document.getElementById("spectator-minimap");
    if (!minimap) return;
    var layout = selectedMapKey ? mapLayoutFor(selectedMapKey) : null;
    if (layout) {
      minimap.style.backgroundImage = "url('/static/maps/" + layout.def.image + "')";
      minimap.style.backgroundSize = "100% 100%";
      minimap.style.backgroundPosition = "center";
      minimap.style.aspectRatio = layout.def.imgW + " / " + layout.def.imgH;
      minimap.style.height = "auto";
    } else {
      minimap.style.backgroundImage = "";
      minimap.style.backgroundSize = "";
      minimap.style.backgroundPosition = "";
      minimap.style.aspectRatio = "";
      minimap.style.height = "";
    }
  }

  function initMapSelect() {
    var field = document.getElementById("spectator-map-select-field");
    var select = document.getElementById("spectator-map-select");
    if (mapKnownFromServer) {
      applyMinimapBackground();
      return;
    }
    if (!field || !select) return;
    var keys = Object.keys(MAP_DEFS).sort(function (a, b) {
      return MAP_DEFS[a].label.localeCompare(MAP_DEFS[b].label);
    });
    keys.forEach(function (key) {
      var opt = document.createElement("option");
      opt.value = key;
      opt.textContent = MAP_DEFS[key].label;
      select.appendChild(opt);
    });
    field.hidden = false;
    select.addEventListener("change", function () {
      selectedMapKey = select.value;
      applyMinimapBackground();
      render();
    });
  }

  function formatMMSS(totalSeconds) {
    var s = Math.max(0, Math.round(totalSeconds || 0));
    var m = Math.floor(s / 60);
    var r = s % 60;
    return (m < 10 ? "0" : "") + m + ":" + (r < 10 ? "0" : "") + r;
  }

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str == null ? "" : String(str);
    return div.innerHTML;
  }

  // ---- engine state: shared by both live polling and replay playback -------

  var zRange = { min: null, max: null };

  function radiusForZ(z) {
    if (typeof z !== "number") return 20;
    if (zRange.min === null || z < zRange.min) zRange.min = z;
    if (zRange.max === null || z > zRange.max) zRange.max = z;
    var span = zRange.max - zRange.min;
    if (span < 1e-6) return 20;
    var t = (z - zRange.min) / span;
    return 14 + t * 16;
  }

  var engine = {
    players: {}, // pid -> {x,y,z}
    playerStats: {}, // pid -> {pid,team,score,kills,deaths,character_id,name}
    activeAbilities: {}, // pid -> {abilityId, abilityName}
    recentKills: [], // [{victimPid, t}]
    activity: [], // [{t, html}] newest-first
    timerSecondsRemaining: null,
    clock: 0,
  };

  function nameForPid(pid) {
    var stats = engine.playerStats[pid];
    return (stats && stats.name) || "#" + pid;
  }

  function resetEngine() {
    engine.players = {};
    engine.playerStats = {};
    engine.activeAbilities = {};
    engine.recentKills = [];
    engine.activity = [];
    engine.timerSecondsRemaining = null;
    engine.clock = 0;
    zRange = { min: null, max: null };
  }

  function pushActivity(html) {
    engine.activity.unshift({ t: engine.clock, html: html });
    if (engine.activity.length > ACTIVITY_LOG_MAX) {
      engine.activity.length = ACTIVITY_LOG_MAX;
    }
  }

  // Ability-active rings and elimination marks aren't tracked server-side —
  // there's no "respawn" event in the feed, so (matching the PoC this ports)
  // elimination is just "there was a kill event in the last N seconds",
  // derived here from the flowing frame stream.
  function processFrame(frame) {
    engine.clock = frame.t || 0;

    (frame.players || []).forEach(function (p) {
      engine.players[p.pid] = { x: p.x, y: p.y, z: p.z };
    });
    (frame.player_stats || []).forEach(function (s) {
      engine.playerStats[s.pid] = s;
    });
    if (typeof frame.timer_seconds_remaining === "number") {
      engine.timerSecondsRemaining = frame.timer_seconds_remaining;
    }

    (frame.abilities || []).forEach(function (a) {
      if (a.activated) {
        engine.activeAbilities[a.pid] = {
          abilityId: a.ability_id,
          abilityName: a.ability_name || "Ability",
        };
        pushActivity(
          '<span class="text-primary">' +
            escapeHtml(nameForPid(a.pid)) +
            "</span> activated <strong>" +
            escapeHtml(a.ability_name || "an ability") +
            "</strong>"
        );
      } else {
        delete engine.activeAbilities[a.pid];
      }
    });

    (frame.kills || []).forEach(function (k) {
      engine.recentKills.push({ victimPid: k.victim_pid, t: engine.clock });
      var killerName = k.killer_pid != null ? nameForPid(k.killer_pid) : "Something";
      pushActivity(
        '<span class="text-loss">' +
          escapeHtml(killerName) +
          "</span> eliminated <strong>" +
          escapeHtml(nameForPid(k.victim_pid)) +
          "</strong>"
      );
    });

    engine.recentKills = engine.recentKills.filter(function (k) {
      return engine.clock - k.t <= DEATH_MARK_SECONDS;
    });
  }

  function isEliminated(pid) {
    return engine.recentKills.some(function (k) {
      return k.victimPid === pid;
    });
  }

  function teamOrder() {
    var teams = [];
    Object.keys(engine.playerStats).forEach(function (pid) {
      var t = engine.playerStats[pid].team;
      if (t !== undefined && t !== null && teams.indexOf(t) === -1) teams.push(t);
    });
    teams.sort();
    return teams;
  }

  function teamClass(team, order) {
    return order.length && order[0] === team ? "team1" : "team2";
  }

  // ---- rendering --------------------------------------------------------

  function render() {
    var order = teamOrder();

    var totals = { team1: 0, team2: 0 };
    Object.keys(engine.playerStats).forEach(function (pid) {
      var s = engine.playerStats[pid];
      totals[teamClass(s.team, order)] += s.score || 0;
    });

    var t1 = document.getElementById("spectator-team1-score");
    var t2 = document.getElementById("spectator-team2-score");
    if (t1) t1.textContent = totals.team1;
    if (t2) t2.textContent = totals.team2;

    var pill = document.getElementById("spectator-lead-pill");
    if (pill) {
      pill.className = "pill";
      if (totals.team1 === totals.team2) {
        pill.classList.add("pill-tie");
        pill.textContent = "Tied";
      } else {
        pill.classList.add("pill-win");
        var leader = totals.team1 > totals.team2 ? "Team 1" : "Team 2";
        pill.textContent = leader + (mode === "replay" ? " Wins" : " Leads");
      }
    }

    var minimap = document.getElementById("spectator-minimap");
    if (minimap) {
      var layout = selectedMapKey ? mapLayoutFor(selectedMapKey) : null;
      var dotsHtml = "";
      Object.keys(engine.players).forEach(function (pidStr) {
        var pid = Number(pidStr);
        var pos = engine.players[pid];
        var stats = engine.playerStats[pid];
        var team = stats ? teamClass(stats.team, order) : "team1";
        var eliminated = isEliminated(pid);
        var abilityActive = !!engine.activeAbilities[pid];
        var radius = radiusForZ(pos.z);
        var initial = stats && stats.name ? stats.name.charAt(0).toUpperCase() : "?";
        var iconUrl = stats ? characterIconUrl(stats.character_id) : null;
        var leftPct = layout ? layout.toXPct(pos.x) : pct(pos.x);
        var topPct = layout ? layout.toYPct(pos.y) : pct(pos.y);
        var classes =
          "spectator-dot spectator-dot-" +
          team +
          (iconUrl ? " spectator-dot-icon" : "") +
          (abilityActive ? " ability-active" : "") +
          (eliminated ? " eliminated" : "");
        dotsHtml +=
          '<div class="' +
          classes +
          '" style="left:' +
          leftPct +
          "%;top:" +
          topPct +
          "%;width:" +
          radius * 2 +
          "px;height:" +
          radius * 2 +
          "px;margin-left:-" +
          radius +
          "px;margin-top:-" +
          radius +
          "px;" +
          (iconUrl ? "background-image:url('" + iconUrl + "');" : "") +
          '">' +
          (iconUrl ? "" : escapeHtml(initial)) +
          (eliminated ? '<div class="spectator-dot-badge">&times;</div>' : "") +
          "</div>";
      });
      minimap.innerHTML = dotsHtml;
    }

    var body = document.getElementById("spectator-roster-body");
    if (body) {
      var rows = Object.keys(engine.playerStats).map(function (pidStr) {
        return engine.playerStats[pidStr];
      });
      rows.sort(function (a, b) {
        return (b.score || 0) - (a.score || 0);
      });

      body.innerHTML = rows
        .map(function (s) {
          var team = teamClass(s.team, order);
          var eliminated = isEliminated(s.pid);
          var ability = engine.activeAbilities[s.pid];
          var statusHtml = "&mdash;";
          if (eliminated) {
            statusHtml = '<span class="text-loss">DOWN</span>';
          } else if (ability) {
            statusHtml = '<span class="text-primary">' + escapeHtml(ability.abilityName) + "</span>";
          }
          var initial = s.name ? s.name.charAt(0).toUpperCase() : "?";
          var className = characterNameFor(s.character_id);
          var iconUrl = characterIconUrl(s.character_id);
          return (
            '<tr><td><div class="spectator-roster-player">' +
            '<div class="spectator-roster-avatar text-' +
            team +
            (iconUrl ? " spectator-roster-avatar-icon" : "") +
            '"' +
            (iconUrl ? ' style="background-image:url(\'' + iconUrl + '\')"' : "") +
            ">" +
            (iconUrl ? "" : escapeHtml(initial)) +
            "</div><div><div class=\"spectator-roster-name\">" +
            escapeHtml(s.name || "Unknown") +
            "</div>" +
            (className ? '<div class="spectator-roster-class">' + escapeHtml(className) + "</div>" : "") +
            "</div></div></td>" +
            '<td><span class="pill spectator-team-pill-' +
            team +
            '">' +
            (team === "team1" ? "Team 1" : "Team 2") +
            "</span></td>" +
            "<td>" + (s.score || 0) + "</td>" +
            "<td>" + (s.kills || 0) + "</td>" +
            "<td>" + (s.deaths || 0) + "</td>" +
            "<td>" + statusHtml + "</td></tr>"
          );
        })
        .join("");
    }

    var activityEl = document.getElementById("spectator-activity");
    if (activityEl) {
      activityEl.innerHTML = engine.activity
        .map(function (a) {
          return (
            '<div class="spectator-activity-row"><span class="spectator-activity-time">' +
            formatMMSS(a.t) +
            "</span><span>" +
            a.html +
            "</span></div>"
          );
        })
        .join("");
    }

    var timerValue = document.getElementById("spectator-timer-value");
    var timerCaption = document.getElementById("spectator-timer-caption");
    if (timerValue) {
      timerValue.textContent =
        engine.timerSecondsRemaining != null ? formatMMSS(engine.timerSecondsRemaining) : "--:--";
    }
    if (timerCaption && mode === "replay") {
      timerCaption.textContent = "Time Remaining · at " + formatMMSS(engine.clock);
    }
  }

  // ---- live mode ----------------------------------------------------------

  function runLive() {
    var pollUrl = root.dataset.pollUrl;
    var intervalMs = parseInt(root.dataset.pollIntervalMs, 10) || 500;
    var sinceSeq = 0;

    var seedEl = document.getElementById("spectator-seed");
    if (seedEl) {
      try {
        var seed = JSON.parse(seedEl.textContent);
        if (seed) {
          processFrame(seed);
          sinceSeq = seed.seq || 0;
          render();
        }
      } catch (e) {
        /* no usable seed, first poll will populate everything */
      }
    }

    function poll() {
      var url =
        pollUrl +
        "?match_id=" +
        encodeURIComponent(root.dataset.matchId) +
        "&since_seq=" +
        sinceSeq;
      fetch(url, { credentials: "same-origin" })
        .then(function (r) {
          if (r.status === 403) {
            // an active participant slipped through to this page somehow
            // (e.g. their roster status changed after load) -- reload so the
            // server re-renders the locked page.
            window.location.reload();
            return null;
          }
          return r.json();
        })
        .then(function (data) {
          if (!data || !data.live) return;
          var frames = data.frames || [];
          frames.forEach(function (f) {
            processFrame(f);
            sinceSeq = f.seq;
          });
          if (frames.length) render();
        })
        .catch(function () {
          /* transient network error -- try again next tick */
        });
    }

    poll();
    setInterval(poll, intervalMs);
  }

  // ---- replay mode ----------------------------------------------------------

  function runReplay() {
    var framesUrl = root.dataset.framesUrl;
    var frames = [];
    var lastProcessedIndex = -1;
    var elapsed = 0;
    var duration = parseFloat(root.dataset.duration) || 0;
    var speed = 1;
    var playing = false;
    var lastTick = null;

    var playBtn = document.getElementById("spectator-play-btn");
    var track = document.getElementById("spectator-scrubber-track");
    var fill = document.getElementById("spectator-scrubber-fill");
    var handle = document.getElementById("spectator-scrubber-handle");
    var elapsedEl = document.getElementById("spectator-elapsed");
    var durationEl = document.getElementById("spectator-duration");

    function frameIndexAtElapsed(t) {
      var lo = 0,
        hi = frames.length - 1,
        ans = -1;
      while (lo <= hi) {
        var mid = (lo + hi) >> 1;
        if (frames[mid].t <= t) {
          ans = mid;
          lo = mid + 1;
        } else {
          hi = mid - 1;
        }
      }
      return ans;
    }

    function applyElapsed(t) {
      elapsed = clamp(t, 0, duration);
      var targetIndex = frameIndexAtElapsed(elapsed);

      if (targetIndex < lastProcessedIndex) {
        // scrubbed backward: there's no "undo", so replay everything up to
        // the target from scratch (same approach the PoC uses).
        resetEngine();
        lastProcessedIndex = -1;
      }
      for (var i = lastProcessedIndex + 1; i <= targetIndex; i++) {
        processFrame(frames[i]);
      }
      lastProcessedIndex = Math.max(lastProcessedIndex, targetIndex);
      engine.clock = elapsed;

      var frac = duration > 0 ? elapsed / duration : 0;
      if (fill) fill.style.width = frac * 100 + "%";
      if (handle) handle.style.left = frac * 100 + "%";
      if (elapsedEl) elapsedEl.textContent = formatMMSS(elapsed);

      render();
    }

    function updatePlayButton() {
      if (!playBtn) return;
      playBtn.classList.toggle("playing", playing);
      playBtn.setAttribute("aria-label", playing ? "Pause" : "Play");
    }

    function tick(now) {
      if (!playing) {
        lastTick = null;
        return;
      }
      if (lastTick == null) lastTick = now;
      var dt = (now - lastTick) / 1000;
      lastTick = now;
      applyElapsed(elapsed + dt * speed);
      if (elapsed >= duration) {
        playing = false;
        updatePlayButton();
        return;
      }
      requestAnimationFrame(tick);
    }

    if (playBtn) {
      playBtn.addEventListener("click", function () {
        playing = !playing;
        updatePlayButton();
        if (playing) {
          lastTick = null;
          requestAnimationFrame(tick);
        }
      });
    }

    if (track) {
      var scrubbing = false;
      var seekFromEvent = function (evt) {
        var rect = track.getBoundingClientRect();
        var clientX = evt.touches ? evt.touches[0].clientX : evt.clientX;
        var frac = clamp((clientX - rect.left) / rect.width, 0, 1);
        applyElapsed(frac * duration);
      };
      track.addEventListener("mousedown", function (evt) {
        scrubbing = true;
        seekFromEvent(evt);
      });
      window.addEventListener("mousemove", function (evt) {
        if (scrubbing) seekFromEvent(evt);
      });
      window.addEventListener("mouseup", function () {
        scrubbing = false;
      });
      track.addEventListener("touchstart", seekFromEvent);
      track.addEventListener("touchmove", seekFromEvent);
    }

    Array.prototype.forEach.call(document.querySelectorAll(".spectator-speed-chip"), function (chip) {
      chip.addEventListener("click", function () {
        speed = parseFloat(chip.dataset.speed) || 1;
        Array.prototype.forEach.call(document.querySelectorAll(".spectator-speed-chip"), function (c) {
          c.classList.toggle("active", c === chip);
        });
      });
    });

    if (durationEl) durationEl.textContent = formatMMSS(duration);

    fetch(framesUrl, { credentials: "same-origin" })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        frames = (data && data.frames) || [];
        if (data && data.duration_s != null) {
          duration = data.duration_s;
          if (durationEl) durationEl.textContent = formatMMSS(duration);
        }
        applyElapsed(0);
      })
      .catch(function () {
        /* nothing to play */
      });
  }

  initMapSelect();

  if (mode === "live") {
    runLive();
  } else if (mode === "replay") {
    runReplay();
  }
})();
