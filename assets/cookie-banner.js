/* Cartesa — bandeau de consentement cookies (RGPD-friendly, sans dépendance) */
(function () {
  'use strict';

  var STORAGE_KEY = 'cartesa-cookie-consent';
  var existing = null;
  try { existing = localStorage.getItem(STORAGE_KEY); } catch (e) { /* localStorage indisponible */ }

  // Si l'utilisateur a déjà choisi, on n'affiche pas le bandeau
  if (existing === 'accepted' || existing === 'refused') return;

  function buildBanner() {
    var banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-live', 'polite');
    banner.setAttribute('aria-label', 'Consentement cookies');
    banner.innerHTML = ''
      + '<div class="cookie-banner__text">'
      + '<strong>Cookies — votre choix.</strong> '
      + 'Nous utilisons uniquement un cookie technique pour mémoriser votre préférence. '
      + 'Aucun traceur publicitaire, aucun outil de mesure d\'audience activé sans votre accord. '
      + '<a href="politique-cookies.html">En savoir plus</a>.'
      + '</div>'
      + '<div class="cookie-banner__actions">'
      + '<button type="button" class="cookie-banner__btn cookie-banner__btn--refuse" data-cc="refuse">Refuser</button>'
      + '<button type="button" class="cookie-banner__btn cookie-banner__btn--accept" data-cc="accept">Accepter</button>'
      + '</div>';
    return banner;
  }

  function setChoice(value) {
    try { localStorage.setItem(STORAGE_KEY, value); } catch (e) {}
    var banner = document.querySelector('.cookie-banner');
    if (banner) banner.classList.remove('is-visible');
    // Hook pour brancher Analytics si "accepted" plus tard :
    if (value === 'accepted') {
      document.dispatchEvent(new CustomEvent('cookies:accepted'));
    } else {
      document.dispatchEvent(new CustomEvent('cookies:refused'));
    }
  }

  function init() {
    var banner = buildBanner();
    document.body.appendChild(banner);
    // Laisser un tick pour que la transition CSS s'applique
    requestAnimationFrame(function () { banner.classList.add('is-visible'); });

    banner.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-cc]');
      if (!btn) return;
      setChoice(btn.getAttribute('data-cc') === 'accept' ? 'accepted' : 'refused');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
