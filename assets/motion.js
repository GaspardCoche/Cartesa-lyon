/* ===== CARTESA — Motion layer (partagée) =====
   1. Scroll-reveal de secours pour les pages sans observer inline (blog, contact, légales)
   2. Compteurs animés sur les stats de hero (.page-hero-stat strong, [data-count])
   Respecte prefers-reduced-motion. Idempotent : peut cohabiter avec les observers inline. */
(function () {
  'use strict';

  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- 1. Scroll-reveal (fallback) --------------------------------- */
  var revealables = document.querySelectorAll(
    '.reveal:not(.revealed), .reveal-left:not(.revealed), .reveal-right:not(.revealed), ' +
    '.reveal-scale:not(.revealed), .reveal-stagger:not(.revealed)'
  );
  if (revealables.length) {
    if (prefersReduced || !('IntersectionObserver' in window)) {
      revealables.forEach(function (el) { el.classList.add('revealed'); });
    } else {
      var revealObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            revealObs.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
      revealables.forEach(function (el) { revealObs.observe(el); });
    }
  }

  /* --- 2. Compteurs animés ------------------------------------------ */
  /* Anime la partie numérique d'un texte de stat ("15j" → 0j…15j, "3 000 €" → …).
     Les valeurs sans chiffre (ex. "CO2I") sont laissées telles quelles. */
  function animateCounter(el) {
    var original = el.textContent;
    var match = original.match(/^([^\d]*)([\d][\d\s ]*)(.*)$/);
    if (!match) return;
    var prefix = match[1];
    var numStr = match[2];
    var suffix = match[3];
    /* Acronymes type "CO2I" : chiffre collé entre deux lettres → ne pas animer */
    if (/[A-Za-z]$/.test(prefix) && /^[A-Za-z]/.test(suffix)) return;
    var target = parseInt(numStr.replace(/[\s ]/g, ''), 10);
    if (isNaN(target) || target === 0) return;
    var useThousands = /[\s ]/.test(numStr);
    var duration = 1100;
    var start = null;

    function fmt(n) {
      if (!useThousands) return String(n);
      return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3); /* easeOutCubic */
      el.textContent = prefix + fmt(Math.round(target * eased)) + suffix;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = original;
    }
    requestAnimationFrame(step);
  }

  var counters = document.querySelectorAll('.page-hero-stat strong, [data-count]');
  if (counters.length && !prefersReduced && 'IntersectionObserver' in window) {
    var countObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          countObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { countObs.observe(el); });
  }
})();
