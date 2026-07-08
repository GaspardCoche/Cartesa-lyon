#!/usr/bin/env python3.12
"""Génère le dossier AUDIT/ : arborescence + inventaire section par section
(ancienne version cartesa-gtm-2026 vs nouvelle cartesa_migration), avec un
emplacement de retour pour CHAQUE section. But : permettre à Gaspard d'annoter
précisément tout ce qui doit changer.
"""
import os
import re
import glob
from html.parser import HTMLParser

NEW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = os.path.expanduser("~/Desktop/projects/Cartesa/cartesa-gtm-2026")
OUT = os.path.join(NEW, "AUDIT")
SKIP = {"script", "style", "nav", "header", "footer", "svg"}

# Ordre logique (menu Proposition 2) + pages de contenu + légal
ORDER = [
    "index.html", "vos-attentes.html", "expertises.html", "coachings.html",
    "formations.html", "ingenierie.html", "rse-decarbonation.html",
    "pourquoi-cartesa.html", "ressourcerie.html", "blog.html", "contact.html",
    "equipe.html", "temoignages.html", "accompagnements.html",
    "mentions-legales.html", "politique-confidentialite.html", "politique-cookies.html",
]
LABEL = {
    "index.html": "Accueil", "vos-attentes.html": "Vos attentes (hub besoins)",
    "expertises.html": "Diagnostic & accompagnements RH", "coachings.html": "Coachings",
    "formations.html": "Formations", "ingenierie.html": "Ingénierie pédagogique",
    "rse-decarbonation.html": "RSE & Décarbonation", "pourquoi-cartesa.html": "Pourquoi CARTESA",
    "ressourcerie.html": "Ressources", "blog.html": "Blog", "contact.html": "Contact",
    "equipe.html": "L'équipe (ancien)", "temoignages.html": "Témoignages (ancien)",
    "accompagnements.html": "Accompagnements (redirigé)",
    "mentions-legales.html": "Mentions légales", "politique-confidentialite.html": "Confidentialité",
    "politique-cookies.html": "Cookies",
}


class Outline(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.cur = None
        self.buf = []
        self.textbuf = []
        self.sec_id = None
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        a = dict(attrs)
        if tag == "section" and a.get("id"):
            self.sec_id = a.get("id")
        if tag in ("h1", "h2", "h3"):
            self._flush()
            self.cur = tag
            self.buf = []

    def handle_endtag(self, tag):
        if tag in SKIP:
            if self.skip:
                self.skip -= 1
            return
        if self.skip:
            return
        if tag in ("h1", "h2", "h3") and self.cur == tag:
            text = " ".join("".join(self.buf).split())
            if text:
                self.items.append({"lvl": int(tag[1]), "text": text, "id": self.sec_id, "content": ""})
            self.cur = None
            self.sec_id = None

    def handle_data(self, data):
        if self.skip:
            return
        (self.buf if self.cur else self.textbuf).append(data)

    def _flush(self):
        if self.items and self.textbuf:
            txt = " ".join("".join(self.textbuf).split())
            if txt:
                self.items[-1]["content"] = (self.items[-1]["content"] + " " + txt).strip()
        self.textbuf = []

    def finish(self):
        self._flush()


def parse(path):
    html = open(path, encoding="utf-8", errors="ignore").read()
    title = ""
    m = re.search(r"<title>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    if m:
        title = " ".join(m.group(1).split())
    p = Outline()
    p.feed(html)
    p.finish()
    return title, p.items


def excerpt(s, n=240):
    s = s.strip()
    return (s[:n] + "…") if len(s) > n else s


def signature(items):
    return [i["text"] for i in items]


os.makedirs(os.path.join(OUT, "pages"), exist_ok=True)

# Parse les deux versions
new_pages = {os.path.basename(p): parse(p) for p in glob.glob(os.path.join(NEW, "*.html"))}
old_pages = {os.path.basename(p): parse(p) for p in glob.glob(os.path.join(OLD, "*.html"))}

# ── README : arborescence + comparaison globale ──
readme = ["# CARTESA — Dossier d'audit du site (retours détaillés)",
          "",
          "> Généré le 2026-07-06. But : voir **toute** l'arborescence et **toutes les sections** "
          "(ancienne version `cartesa-gtm-2026` ↔ nouvelle `cartesa_migration`), et donner un retour "
          "précis sur chaque section / chaque contenu.",
          "",
          "## Comment l'utiliser",
          "Ouvre un fichier par page dans `AUDIT/pages/`. Pour chaque section, écris ton retour sous "
          "la ligne `**Retour :**`. Tu peux tout annoter : titre, texte, ordre, à supprimer, à ajouter…",
          "",
          "## Arborescence — menu (nouvelle version, Proposition 2 retenue)",
          "```",
          "Accueil",
          "Vos attentes ▾  →  Structurer & fidéliser · Développer vos managers · Former vos équipes · Décarboner",
          "Nos expertises ▾  →  Diagnostic & accompagnements · Coachings · Formations · Ingénierie · RSE & Décarbonation",
          "Pourquoi CARTESA",
          "Ressources",
          "Contact",
          "```",
          "",
          "## Pages : ancien → nouveau",
          "",
          "| Page | Ancienne version | Nouvelle version | Évolution |",
          "|------|:---------------:|:----------------:|-----------|"]

status = {
    "index.html": "Conservée, en-tête/pied unifiés",
    "vos-attentes.html": "**NOUVELLE** (hub besoins, Proposition 2)",
    "expertises.html": "**FUSIONNÉE** : Diagnostic + Accompagnements",
    "coachings.html": "**NOUVELLE** (coachings regroupés)",
    "formations.html": "Conservée",
    "ingenierie.html": "Conservée",
    "rse-decarbonation.html": "Conservée",
    "pourquoi-cartesa.html": "**NOUVELLE** = fusion Équipe + Témoignages",
    "ressourcerie.html": "Conservée (auto-diagnostics à activer)",
    "blog.html": "Conservée",
    "contact.html": "Conservée",
    "equipe.html": "Contenu déplacé → Pourquoi CARTESA",
    "temoignages.html": "Contenu déplacé → Pourquoi CARTESA",
    "accompagnements.html": "**REDIRIGÉE** → expertises.html",
    "mentions-legales.html": "Conservée", "politique-confidentialite.html": "Conservée",
    "politique-cookies.html": "Conservée",
}
for page in ORDER:
    o = "✓" if page in old_pages else "—"
    n = "✓" if page in new_pages else "—"
    readme.append(f"| `{page}` — {LABEL.get(page, page)} | {o} | {n} | {status.get(page,'')} |")

readme += ["", "## Sommaire des fiches de retour", ""]
for page in ORDER:
    if page in new_pages or page in old_pages:
        readme.append(f"- [{LABEL.get(page, page)}](pages/{page.replace('.html','')}.md) (`{page}`)")

open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write("\n".join(readme))

# ── Une fiche par page ──
def render_items(items):
    lines = []
    for it in items:
        indent = "  " * (it["lvl"] - 1)
        anchor = f" `#{it['id']}`" if it.get("id") else ""
        hn = "#" * min(4, it["lvl"] + 2)
        lines.append(f"{hn} {it['text']}{anchor}")
        if it["content"]:
            lines.append(f"> {excerpt(it['content'])}")
        lines.append("")
        lines.append("**Retour :** ")
        lines.append("")
        lines.append("---")
        lines.append("")
    return lines

pages_seen = set()
for page in ORDER + [p for p in sorted(set(new_pages) | set(old_pages)) if p not in ORDER]:
    if page in pages_seen or (page not in new_pages and page not in old_pages):
        continue
    pages_seen.add(page)
    out = [f"# {LABEL.get(page, page)} — `{page}`", ""]
    if page in new_pages:
        title, items = new_pages[page]
        out += [f"*Titre de page :* {title}", "", f"*Statut :* {status.get(page,'')}", "",
                "## Sections (nouvelle version)", ""]
        out += render_items(items) if items else ["_(page de redirection ou sans sections de contenu)_", ""]
    # Diff avec l'ancienne version
    if page in old_pages:
        _, old_items = old_pages[page]
        new_sig = set(signature(new_pages[page][1])) if page in new_pages else set()
        old_sig = signature(old_items)
        removed = [t for t in old_sig if t not in new_sig]
        if page not in new_pages:
            out += ["## Sections (ancienne version — page non reprise telle quelle)", ""]
            out += render_items(old_items)
        elif removed:
            out += ["## ⚠️ Sections de l'ANCIENNE version absentes de la nouvelle (à arbitrer)", ""]
            for t in removed:
                out.append(f"- {t}")
            out += ["", "**Retour :** (garder / supprimer / déplacer ?)", "", "---", ""]
    else:
        out += ["*(Page nouvelle — pas d'équivalent dans l'ancienne version.)*", ""]
    open(os.path.join(OUT, "pages", page.replace(".html", ".md")), "w", encoding="utf-8").write("\n".join(out))

print("AUDIT généré :")
print(" - README.md")
print(f" - {len(pages_seen)} fiches dans pages/")
