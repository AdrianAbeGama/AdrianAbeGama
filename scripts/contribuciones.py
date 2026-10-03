"""Panel animado de contribuciones del último año (lo corre GitHub Actions cada día).

Lee el calendario de contribuciones por GraphQL (con GITHUB_TOKEN, o con `gh` si se corre a mano)
y dibuja las cifras y el mapa de cuadritos con el estilo de la portada. Solo usa la librería estándar.

Uso: python scripts/contribuciones.py salida.svg
"""
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request

USUARIO = os.environ.get("USUARIO", "AdrianAbeGama")
CONSULTA = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount weekday}}}}}}"""

MONO = "Consolas, 'Cascadia Mono', 'SF Mono', Menlo, 'DejaVu Sans Mono', monospace"
FONDO, VENT, BORDE, BARRA = "#070b14", "#0b111d", "#1e2a3d", "#101827"
TEXTO, SUAVE, TENUE, AZUL = "#e8eef7", "#94a0b4", "#5a6880", "#4d9fff"
NIVELES = ["#111a2b", "#12305a", "#1a4d8f", "#2f74c8", "#4d9fff"]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
W = 1200


def calendario():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        pedido = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": CONSULTA, "variables": {"u": USUARIO}}).encode(),
            headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
        )
        datos = json.load(urllib.request.urlopen(pedido))
    else:  # a mano, con la sesión de GitHub CLI
        datos = json.loads(subprocess.check_output(["gh", "api", "graphql", "-f", f"query={CONSULTA}", "-f", f"u={USUARIO}"]))
    return datos["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def racha_mas_larga(dias):
    larga = actual = 0
    for d in dias:
        actual = actual + 1 if d["contributionCount"] else 0
        larga = max(larga, actual)
    return larga


def fecha_corta(iso):
    f = dt.date.fromisoformat(iso)
    return f"{f.day} {MESES[f.month - 1]}"


def dibujar(cal):
    semanas = cal["weeks"]
    dias = [d for s in semanas for d in s["contributionDays"]]
    total = cal["totalContributions"]
    larga = racha_mas_larga(dias)
    activos = sum(1 for d in dias if d["contributionCount"])
    mejor = max(dias, key=lambda d: d["contributionCount"])
    con = sorted(d["contributionCount"] for d in dias if d["contributionCount"])
    cortes = [con[int(len(con) * q)] for q in (0.25, 0.5, 0.75)] if con else [1, 2, 3]

    def nivel(n):
        return 0 if n == 0 else 1 + sum(n > c for c in cortes)

    H, celda, gap = 470, 16, 4
    x0 = (W - len(semanas) * (celda + gap) + gap) // 2
    y0 = 272
    cuadros, meses, ultimo_mes, col_mes = [], [], None, -9
    for c, s in enumerate(semanas):
        primero = s["contributionDays"][0]["date"]
        mes = int(primero[5:7])
        if mes != ultimo_mes and c < len(semanas) - 2:
            if c - col_mes < 3 and meses:  # el mes anterior apenas asomó: su etiqueta se encimaría
                meses.pop()
            col_mes = c
            meses.append(f'<text x="{x0 + c*(celda+gap)}" y="{y0-12}" font-size="14" fill="{TENUE}">{MESES[mes-1]}</text>')
        ultimo_mes = mes
        for d in s["contributionDays"]:
            f = d["weekday"]
            n = d["contributionCount"]
            cuadros.append(f'<rect class="c" style="animation-delay:{0.9 + c*0.014 + f*0.03:.2f}s" x="{x0 + c*(celda+gap)}" y="{y0 + f*(celda+gap)}" '
                           f'width="{celda}" height="{celda}" rx="3" fill="{NIVELES[nivel(n)]}"><title>{d["date"]}: {n}</title></rect>')
    ancho_mapa = len(semanas) * (celda + gap) - gap
    cifras = [(f"{total:,}", "contribuciones en el año", AZUL), (f"{larga}", "días de racha más larga", TEXTO),
              (f"{activos}", "días programando", TEXTO), (f"{mejor['contributionCount']}", f"en un día · {fecha_corta(mejor['date'])}", TEXTO)]
    bloques = ""
    ancho_b = (ancho_mapa - 3 * 16) / 4
    for i, (num, txt, color) in enumerate(cifras):
        x = x0 + i * (ancho_b + 16)
        bloques += f'''<g class="sube" style="animation-delay:{0.35 + i*0.12:.2f}s">
<rect x="{x:.0f}" y="132" width="{ancho_b:.0f}" height="84" rx="12" fill="{VENT}" stroke="{BORDE}" stroke-width="1.5"/>
<text x="{x+20:.0f}" y="178" font-size="34" fill="{color}" font-weight="bold">{num}</text>
<text x="{x+20:.0f}" y="202" font-size="14" fill="{SUAVE}">{txt}</text></g>'''
    leyenda = "".join(f'<rect x="{x0 + ancho_mapa - 5*(celda+gap) + i*(celda+gap) - 40}" y="{y0 + 7*(celda+gap) + 16}" width="{celda}" height="{celda}" rx="3" fill="{c}"/>' for i, c in enumerate(NIVELES))
    yl = y0 + 7 * (celda + gap) + 29
    hoy_txt = dt.date.today().isoformat()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">
<style>
.ap{{opacity:0;animation:ap .4s forwards}}
.sube{{opacity:0;transform:translateY(12px);animation:sube .6s cubic-bezier(.2,.8,.2,1) forwards}}
.c{{opacity:0;animation:ap .35s forwards}}
.scan{{animation:scan 6s linear 3s infinite;opacity:0}}
.pulso{{animation:pulso 2s ease-in-out infinite}}
@keyframes ap{{to{{opacity:1}}}}
@keyframes sube{{to{{opacity:1;transform:none}}}}
@keyframes scan{{0%{{transform:translateX(0);opacity:1}}100%{{transform:translateX({ancho_mapa + 80}px);opacity:1}}}}
@keyframes pulso{{50%{{opacity:.35}}}}
</style>
<defs>
  <pattern id="puntos" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#16213a"/></pattern>
  <radialGradient id="luz" cx="50%" cy="0%" r="70%"><stop offset="0" stop-color="{AZUL}" stop-opacity=".14"/><stop offset="1" stop-color="{AZUL}" stop-opacity="0"/></radialGradient>
  <linearGradient id="barrido" x1="0" x2="1"><stop offset="0" stop-color="{AZUL}" stop-opacity="0"/><stop offset=".5" stop-color="{AZUL}" stop-opacity=".22"/><stop offset="1" stop-color="{AZUL}" stop-opacity="0"/></linearGradient>
  <clipPath id="mapa"><rect x="{x0}" y="{y0}" width="{ancho_mapa}" height="{7*(celda+gap)}"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="{FONDO}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#puntos)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#luz)"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="{BORDE}" stroke-width="2"/>
<circle cx="34" cy="34" r="7" fill="#ff5f57"/><circle cx="58" cy="34" r="7" fill="#febc2e"/><circle cx="82" cy="34" r="7" fill="#28c840"/>
<text x="108" y="40" font-size="18" fill="{TENUE}">~/actividad — git log</text>
<text x="{W-32}" y="40" font-size="18" fill="{TENUE}" text-anchor="end"><tspan class="pulso" fill="{AZUL}">●</tspan> en vivo · {hoy_txt}</text>
<line x1="2" y1="64" x2="{W-2}" y2="64" stroke="{BORDE}" stroke-width="2"/>
<text class="ap" x="{x0}" y="106" font-size="18" fill="{AZUL}">$ <tspan fill="{TEXTO}">git log --author="adrian" --since="1 year ago" | wc -l</tspan></text>
{bloques}
{"".join(meses)}
{"".join(cuadros)}
<g clip-path="url(#mapa)"><rect class="scan" x="{x0 - 80}" y="{y0}" width="80" height="{7*(celda+gap)}" fill="url(#barrido)"/></g>
<text x="{x0}" y="{yl}" font-size="14" fill="{TENUE}"># se regenera solo cada día · GitHub Actions + GraphQL · incluye repos privados</text>
<text x="{x0 + ancho_mapa - 5*(celda+gap) - 52}" y="{yl}" font-size="14" fill="{TENUE}" text-anchor="end">menos</text>
{leyenda}
<text x="{x0 + ancho_mapa}" y="{yl}" font-size="14" fill="{TENUE}" text-anchor="end">más</text>
</svg>'''


if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else "contribuciones.svg"
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    with open(salida, "w", encoding="utf-8") as f:
        f.write(dibujar(calendario()))
    print("ok", salida)
