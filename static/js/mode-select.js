// Persistent Game -> Mode selector shared by the leaderboard and profile pages.
// Selection is stored in cookies so it carries over between the two page types.
(function () {
  // Artifact Assault is rated per game, so each game has its own AA modes.
  var GAMES = {
    ACB: { label: "AC Brotherhood", modes: ["Escort", "Manhunt", "Assassinate"] },
    ACR: { label: "AC Revelations", modes: ["ACR AA Running", "ACR AA Defending"] },
    AC3: { label: "AC III", modes: ["AC3 AA Running", "AC3 AA Defending", "Domination"] },
    AC4: { label: "AC IV", modes: ["AC4 AA Running", "AC4 AA Defending", "Domination", "Deathmatch"] },
  };
  var MODE_LABELS = {
    "Escort": "Escort", "Manhunt": "Manhunt", "Assassinate": "Assassinate",
    "Domination": "Domination", "Deathmatch": "Deathmatch",
  };
  var MODE_ROUTES = {
    "Escort": "/escort", "Manhunt": "/manhunt", "Assassinate": "/assassinate",
    "Domination": "/domination", "Deathmatch": "/deathmatch",
  };
  ["ACR", "AC3", "AC4"].forEach(function (game) {
    var prefix = game + " ";
    var path = "/" + game.toLowerCase();
    MODE_LABELS[prefix + "AA Running"] = "Artifact Assault (Running)";
    MODE_LABELS[prefix + "AA Defending"] = "Artifact Assault (Defending)";
    MODE_ROUTES[prefix + "AA Running"] = path + "/running";
    MODE_ROUTES[prefix + "AA Defending"] = path + "/defending";
  });
  // ACR's AA modes before they were named after the game (still in cookies)
  var LEGACY_MODES = { "AA Running": "ACR AA Running", "AA Defending": "ACR AA Defending" };
  var DEFAULT_GAME = "ACB", DEFAULT_MODE = "Escort";

  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[1]) : null;
  }
  function setCookie(name, value) {
    document.cookie = name + "=" + encodeURIComponent(value) + ";path=/;max-age=" + 60 * 60 * 24 * 365 + ";samesite=lax";
  }
  function gameForMode(mode) {
    for (var g in GAMES) {
      if (GAMES[g].modes.indexOf(mode) !== -1) return g;
    }
    return DEFAULT_GAME;
  }

  window.ANModeSelect = {
    MODE_ROUTES: MODE_ROUTES,
    init: function (root, opts) {
      opts = opts || {};
      var gameSel = root.querySelector("[data-role=game]");
      var modeSel = root.querySelector("[data-role=mode]");

      var cookieMode = getCookie("an_mode");
      cookieMode = LEGACY_MODES[cookieMode] || cookieMode;
      var initialMode = opts.currentMode && MODE_LABELS[opts.currentMode] ? opts.currentMode : (cookieMode || DEFAULT_MODE);
      // Several modes (Artifact Assault, Domination, ...) are shared across more than one
      // game. Keep the previously chosen game if it's still compatible with initialMode,
      // instead of always collapsing back to that mode's first/default game.
      var cookieGame = getCookie("an_game");
      var initialGame;
      if (cookieGame && GAMES[cookieGame] && GAMES[cookieGame].modes.indexOf(initialMode) !== -1) {
        initialGame = cookieGame;
      } else {
        initialGame = gameForMode(initialMode);
      }
      if (!GAMES[initialGame]) initialGame = DEFAULT_GAME;

      function fillModes(game, selectedMode) {
        modeSel.innerHTML = "";
        GAMES[game].modes.forEach(function (m) {
          var opt = document.createElement("option");
          opt.value = m;
          opt.textContent = MODE_LABELS[m];
          if (m === selectedMode) opt.selected = true;
          modeSel.appendChild(opt);
        });
        if (modeSel.selectedIndex === -1) modeSel.selectedIndex = 0;
      }

      gameSel.value = initialGame;
      fillModes(initialGame, GAMES[initialGame].modes.indexOf(initialMode) !== -1 ? initialMode : GAMES[initialGame].modes[0]);
      setCookie("an_game", initialGame);
      setCookie("an_mode", modeSel.value);
      if (opts.onReady) opts.onReady(modeSel.value);

      gameSel.addEventListener("change", function () {
        fillModes(gameSel.value, GAMES[gameSel.value].modes[0]);
        setCookie("an_game", gameSel.value);
        setCookie("an_mode", modeSel.value);
        if (opts.onChange) opts.onChange(modeSel.value);
      });
      modeSel.addEventListener("change", function () {
        setCookie("an_game", gameSel.value);
        setCookie("an_mode", modeSel.value);
        if (opts.onChange) opts.onChange(modeSel.value);
      });
    },
  };
})();
