"""Rend un visuel HTML en PNG 1080 x 1350 et signale ce qui déborde.

Usage : /usr/bin/python3 rendre.py posts/2026-10-15.html images/2026-10-15.png
Le commentaire <!--PIED--> du HTML est remplacé par gabarits/pied.html.
"""
import os, sys, tempfile
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
source, sortie = sys.argv[1], sys.argv[2]
html = open(source, encoding="utf-8").read()
html = html.replace("<!--PIED-->", open(os.path.join(ICI, "gabarits", "pied.html"), encoding="utf-8").read())
tmp = os.path.join(os.path.dirname(os.path.abspath(source)), "_rendu.html")
open(tmp, "w", encoding="utf-8").write(html)

VERIF = """() => {
  const limite = (document.querySelector('.sources') || document.querySelector('.pied')).getBoundingClientRect().top;
  const pb = [];
  document.querySelectorAll('.haut *, .contenu *').forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.bottom > limite + 1) pb.push(`${e.tagName}.${e.className} descend à ${Math.round(r.bottom)} px (limite ${Math.round(limite)})`);
    if (r.right > 1080 - 40) pb.push(`${e.tagName}.${e.className} dépasse à droite (${Math.round(r.right)} px)`);
  });
  return [...new Set(pb)].slice(0, 10);
}"""

with sync_playwright() as p:
    nav = p.chromium.launch()
    page = nav.new_page(viewport={"width": 1080, "height": 1350})
    page.goto("file://" + tmp)
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    problemes = page.evaluate(VERIF)
    page.screenshot(path=sortie)
    nav.close()
os.remove(tmp)

if problemes:
    print("DÉBORDEMENT, raccourcissez le texte ou réduisez les tailles :")
    print("\n".join(problemes))
    sys.exit(1)
print("OK", sortie)
