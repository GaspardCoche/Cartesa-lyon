#!/usr/bin/env python3.12
"""Applique une coquille cohérente (Proposition 2) à toutes les pages du site :
- nav P2 unifiée (wordmark, 2 menus : Vos attentes / Nos expertises)
- footer unifié (wordmark, adresse corrigée « près de Lyon », Qualiopi local)
- neutralise les images cassées pointant vers cartesa-lyon.com (logo → wordmark,
  logos partenaires → badges texte)
Idempotent : relançable.
"""
import re
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADER = '''<header class="site-header" id="siteHeader">
    <nav class="nav-inner">
      <a href="index.html" class="nav-logo"><span class="logo-word">CARTESA</span></a>
      <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="navLinks">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links" id="navLinks">
        <li><a href="index.html">Accueil</a></li>
        <li class="nav-dropdown"><a href="vos-attentes.html" aria-haspopup="true" aria-expanded="false">Vos attentes</a>
          <ul class="nav-sub">
            <li><a href="vos-attentes.html#fideliser">Structurer &amp; fid&eacute;liser vos &eacute;quipes</a></li>
            <li><a href="vos-attentes.html#dirigeants">D&eacute;velopper vos dirigeants &amp; managers</a></li>
            <li><a href="vos-attentes.html#former">Former vos &eacute;quipes</a></li>
            <li><a href="vos-attentes.html#decarboner">D&eacute;carboner votre activit&eacute;</a></li>
          </ul>
        </li>
        <li class="nav-dropdown"><a href="expertises.html" aria-haspopup="true" aria-expanded="false">Nos expertises</a>
          <ul class="nav-sub">
            <li><a href="expertises.html">Diagnostic &amp; accompagnements RH</a></li>
            <li><a href="coachings.html">Coachings</a></li>
            <li><a href="formations.html">Formations</a></li>
            <li><a href="ingenierie.html">Ing&eacute;nierie p&eacute;dagogique</a></li>
            <li><a href="rse-decarbonation.html">RSE &amp; D&eacute;carbonation</a></li>
          </ul>
        </li>
        <li><a href="pourquoi-cartesa.html">Pourquoi CARTESA</a></li>
        <li><a href="ressourcerie.html">Ressources</a></li>
        <li><a href="contact.html" class="nav-cta">Contact</a></li>
      </ul>
    </nav>
  </header>'''

FOOTER = '''<footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <span class="logo-word logo-word--light">CARTESA</span>
          <p class="footer-tag">Compétences, Entreprises &amp; Territoires</p>
          <div class="footer-qualiopi">
            <img src="assets/img/qualiopi.jpg" alt="Certifié Qualiopi" width="120" height="60" loading="lazy" decoding="async">
            <span>Certifié Qualiopi au titre des actions de formation</span>
          </div>
        </div>
        <div class="footer-col">
          <h4>Vos attentes</h4>
          <ul>
            <li><a href="vos-attentes.html#fideliser">Structurer &amp; fidéliser</a></li>
            <li><a href="vos-attentes.html#dirigeants">Développer vos managers</a></li>
            <li><a href="vos-attentes.html#former">Former vos équipes</a></li>
            <li><a href="vos-attentes.html#decarboner">Décarboner</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Nos expertises</h4>
          <ul>
            <li><a href="expertises.html">Diagnostic &amp; accompagnements</a></li>
            <li><a href="coachings.html">Coachings</a></li>
            <li><a href="formations.html">Formations</a></li>
            <li><a href="ingenierie.html">Ingénierie pédagogique</a></li>
            <li><a href="rse-decarbonation.html">RSE &amp; Décarbonation</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>CARTESA</h4>
          <ul>
            <li><a href="pourquoi-cartesa.html">Pourquoi CARTESA</a></li>
            <li><a href="ressourcerie.html">Ressources</a></li>
            <li><a href="contact.html">Contact</a></li>
            <li><a href="mentions-legales.html">Mentions légales</a></li>
            <li><a href="politique-confidentialite.html">Confidentialité</a></li>
            <li><a href="politique-cookies.html">Cookies</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Contact</h4>
          <div class="footer-contact-item">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" transform="scale(0.7)"/><circle cx="8.4" cy="7" r="2.1"/></svg>
            <span>Près de Lyon<br>entre Lyon, Grenoble et Chambéry<br><small>Déplacements France &amp; Europe</small></span>
          </div>
          <div class="footer-contact-item">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            <a href="contact.html">Nous contacter</a>
          </div>
          <div class="footer-contact-item">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="1.5" y="3.5" width="13" height="9" rx="1.5"/><path d="M1.5 3.5l6.5 5 6.5-5"/></svg>
            <a href="mailto:contact@cabinet-cartesa.com">contact@cabinet-cartesa.com</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; 2026 CARTESA. Tous droits réservés.</span>
        <div class="footer-bottom__social">
          <a href="https://www.linkedin.com/company/cartesa" target="_blank" rel="noopener" aria-label="LinkedIn CARTESA">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.56c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.13 1.45-2.13 2.94v5.65H9.35V9h3.42v1.56h.05c.48-.9 1.65-1.85 3.4-1.85 3.63 0 4.3 2.39 4.3 5.5v6.24zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.78C.8 0 0 .77 0 1.72v20.56C0 23.23.8 24 1.78 24h20.44c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0z"/></svg>
            LinkedIn
          </a>
        </div>
      </div>
    </div>
  </footer>'''

hdr_re = re.compile(r'<header class="site-header".*?</header>', re.DOTALL)
ftr_re = re.compile(r'<footer class="site-footer">.*?</footer>', re.DOTALL)
# Logo cassé résiduel (hors header/footer déjà remplacés)
logo_img_re = re.compile(r'<img[^>]*src="https://(?:preprod\.)?cartesa-lyon\.com/wp-content/uploads/[^"]*logo[^"]*"[^>]*>', re.IGNORECASE)
# Logos partenaires cassés → badge texte (garde le alt comme libellé)
partner_img_re = re.compile(r'<img[^>]*src="https://(?:preprod\.)?cartesa-lyon\.com/wp-content/uploads/[^"]*"[^>]*alt="([^"]*)"[^>]*>', re.IGNORECASE)

changed = []
for path in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
    src = open(path, encoding='utf-8').read()
    out = src
    if hdr_re.search(out):
        out = hdr_re.sub(lambda m: HEADER, out, count=1)
    if ftr_re.search(out):
        out = ftr_re.sub(lambda m: FOOTER, out, count=1)
    # Neutralise le logo cassé restant → wordmark
    out = logo_img_re.sub('<span class="logo-word">CARTESA</span>', out)
    # Logos partenaires cassés → badge texte
    out = partner_img_re.sub(lambda m: f'<span class="partner-badge">{m.group(1) or "Partenaire"}</span>', out)
    if out != src:
        open(path, 'w', encoding='utf-8').write(out)
        changed.append(os.path.basename(path))

print("Pages mises à jour:", ", ".join(changed) if changed else "(aucune)")
# Vérif : reste-t-il des refs image cartesa-lyon.com ?
import subprocess
r = subprocess.run(['grep', '-rloE', r'src="https://(preprod\.)?cartesa-lyon\.com'] + sorted(glob.glob(os.path.join(ROOT, '*.html'))), capture_output=True, text=True)
print("Pages avec images cassées restantes:", r.stdout.strip() or "(aucune)")
