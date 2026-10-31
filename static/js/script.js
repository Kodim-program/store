/* Слайдер на головній сторінці */
(function () {
  var slides = document.querySelectorAll(".slide"),
      dots = document.getElementById("dots");
  if (!slides.length || !dots) return;
  var cur = 0;
  function go(i) {
    cur = i;
    slides.forEach(function (s, j) { s.classList.toggle("on", j === i); });
    Array.prototype.forEach.call(dots.children, function (d, j) { d.classList.toggle("on", j === i); });
  }
  slides.forEach(function (_, i) {
    var b = document.createElement("button");
    b.type = "button";
    b.setAttribute("aria-label", "Слайд " + (i + 1));
    b.onclick = function () { go(i); };
    dots.appendChild(b);
  });
  go(0);
  setInterval(function () { go((cur + 1) % slides.length); }, 5000);
})();
