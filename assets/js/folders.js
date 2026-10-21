/* Review folders (see /assets/css/folders.css). One folder open at a time; the open folder grows to fit its quote.
   The first folder in each group opens by itself the first time the group scrolls into view, to show how it works. */
(function () {
  "use strict";
  var CLOSED = 184;
  document.querySelectorAll(".fds").forEach(function (group) {
    var folders = Array.prototype.slice.call(group.querySelectorAll(".fd"));
    function openHeight(fd) {
      var paper = fd.querySelector(".fd-paper");
      var h = 0; Array.prototype.forEach.call(paper.children, function (c) { h += c.offsetHeight + parseFloat(getComputedStyle(c).marginBottom || 0); });
      return Math.max(CLOSED, 34 + 16 + h + 22 + 50);
    }
    function set(fd, open) {
      fd.classList.toggle("open", open);
      fd.style.height = open ? openHeight(fd) + "px" : "";
      var t = fd.querySelector(".fd-toggle");
      t.setAttribute("aria-expanded", open ? "true" : "false");
      t.setAttribute("aria-label", (open ? "Close review from " : "Open review from ") + t.dataset.who);
    }
    function toggle(fd) {
      var open = !fd.classList.contains("open");
      folders.forEach(function (f) { if (f !== fd && f.classList.contains("open")) set(f, false); });
      set(fd, open);
    }
    folders.forEach(function (fd) {
      fd.addEventListener("click", function (e) { if (e.target.closest("a")) return; toggle(fd); });
      fd.querySelector(".fd-toggle").addEventListener("click", function (e) { e.stopPropagation(); toggle(fd); });
    });
    addEventListener("resize", function () { folders.forEach(function (f) { if (f.classList.contains("open")) f.style.height = openHeight(f) + "px"; }); });
    // "See all reviews"
    var more = group.parentNode.querySelector(".fds-more button");
    // phones start with 4 folders
    if (more && matchMedia("(max-width: 640px)").matches) folders.forEach(function (f, i) { if (i >= 4) f.hidden = true; });
    if (more) more.addEventListener("click", function () {
      folders.forEach(function (f) { f.hidden = false; });
      more.parentNode.remove();
    });
    // show the interaction once
    if ("IntersectionObserver" in window && folders[0]) {
      var io = new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) { io.disconnect(); setTimeout(function () { if (!group.querySelector(".fd.open")) set(folders[0], true); }, 450); }
      }, { threshold: 0.9 });
      io.observe(folders[0]);
    }
  });
})();
