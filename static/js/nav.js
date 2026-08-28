// Lightweight replacement for Bootstrap's dropdown/collapse/tab JS plugins.
// Avoids depending on jQuery + Popper + bootstrap.min.js loading correctly
// from three chained CDNs just to toggle a couple of "show" classes.
(function () {
  function closeAllDropdowns(except) {
    document.querySelectorAll(".dropdown-menu.show").forEach(function (menu) {
      if (menu !== except) {
        menu.classList.remove("show");
        var toggle = menu.previousElementSibling;
        if (toggle) toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  document.addEventListener("click", function (e) {
    var toggle = e.target.closest('[data-toggle="dropdown"]');
    if (toggle) {
      e.preventDefault();
      var menu = toggle.nextElementSibling;
      if (!menu || !menu.classList.contains("dropdown-menu")) return;
      var isOpen = menu.classList.contains("show");
      closeAllDropdowns(isOpen ? null : menu);
      menu.classList.toggle("show", !isOpen);
      toggle.setAttribute("aria-expanded", String(!isOpen));
      return;
    }
    if (!e.target.closest(".dropdown-menu")) closeAllDropdowns();

    var collapseToggle = e.target.closest('[data-toggle="collapse"]');
    if (collapseToggle) {
      e.preventDefault();
      var targetSel = collapseToggle.getAttribute("data-target") || collapseToggle.getAttribute("href");
      var target = targetSel && document.querySelector(targetSel);
      if (!target) return;
      var nowShown = !target.classList.contains("show");
      target.classList.toggle("show", nowShown);
      collapseToggle.setAttribute("aria-expanded", String(nowShown));
      return;
    }

    var tabToggle = e.target.closest('[data-toggle="tab"]');
    if (tabToggle) {
      e.preventDefault();
      var pane = document.querySelector(tabToggle.getAttribute("href"));
      if (!pane) return;
      var tabList = tabToggle.closest(".nav-tabs");
      var paneContainer = pane.parentElement;
      if (tabList) {
        tabList.querySelectorAll(".nav-link.active").forEach(function (l) { l.classList.remove("active"); });
        tabToggle.classList.add("active");
      }
      if (paneContainer) {
        paneContainer.querySelectorAll(":scope > .tab-pane.active").forEach(function (p) { p.classList.remove("active", "show"); });
      }
      pane.classList.add("active", "show");
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAllDropdowns();
  });
})();
