"""Genera los paneles animados (SVG) de la portada del perfil.

Estilo AbeGama.OS: fondo #070b14 con puntos, ventanas de terminal, Consolas, acento #4d9fff.
Las capturas de los proyectos se incrustan en base64 (un <img> de GitHub no carga archivos externos).

Uso: python scripts/portada.py <carpeta public/projects del portafolio>
"""
import base64
import io
import os
import sys
from xml.sax.saxutils import escape

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "..", "assets")
FOTOS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "capturas")

MONO = "Consolas, 'Cascadia Mono', 'SF Mono', Menlo, 'DejaVu Sans Mono', monospace"
FONDO, VENT, BORDE, BARRA = "#070b14", "#0b111d", "#1e2a3d", "#101827"
TEXTO, SUAVE, TENUE, AZUL, AMBAR, VERDE = "#e8eef7", "#94a0b4", "#5a6880", "#4d9fff", "#ffb142", "#39d353"
W = 1200


def guardar(nombre, svg):
    with open(os.path.join(SALIDA, nombre), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{nombre}: {len(svg) // 1024} KB")


def svg(h, cuerpo, css=""):
    """Panel base: fondo con puntos, brillo arriba y borde."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{MONO}">
<style>
.ap{{opacity:0;animation:ap .5s cubic-bezier(.2,.8,.2,1) forwards}}
.sube{{opacity:0;transform:translateY(14px);animation:sube .6s cubic-bezier(.2,.8,.2,1) forwards}}
.cursor{{animation:parpadeo 1.1s steps(1) infinite}}
.pulso{{animation:pulso 2s ease-in-out infinite}}
.px{{opacity:0;animation:ap .08s forwards}}
@keyframes ap{{to{{opacity:1}}}}
@keyframes sube{{to{{opacity:1;transform:none}}}}
@keyframes parpadeo{{50%{{opacity:0}}}}
@keyframes pulso{{50%{{opacity:.35}}}}
{css}
</style>
<defs>
  <pattern id="puntos" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#16213a"/></pattern>
  <radialGradient id="luz" cx="50%" cy="0%" r="70%"><stop offset="0" stop-color="{AZUL}" stop-opacity=".14"/><stop offset="1" stop-color="{AZUL}" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{h}" rx="18" fill="{FONDO}"/>
<rect width="{W}" height="{h}" rx="18" fill="url(#puntos)"/>
<rect width="{W}" height="{h}" rx="18" fill="url(#luz)"/>
<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="17" fill="none" stroke="{BORDE}" stroke-width="2"/>
{cuerpo}
</svg>'''


def barra(titulo, derecha=""):
    """Barra de ventana: tres puntos, ruta y un dato a la derecha."""
    return f'''<circle cx="34" cy="34" r="7" fill="#ff5f57"/><circle cx="58" cy="34" r="7" fill="#febc2e"/><circle cx="82" cy="34" r="7" fill="#28c840"/>
<text x="108" y="40" font-size="18" fill="{TENUE}">{escape(titulo)}</text>
<text x="{W-32}" y="40" font-size="18" fill="{TENUE}" text-anchor="end">{escape(derecha)}</text>
<line x1="2" y1="64" x2="{W-2}" y2="64" stroke="{BORDE}" stroke-width="2"/>'''


def d(seg):
    return f'style="animation-delay:{seg:.2f}s"'


def b64(ruta, ancho, alto):
    im = Image.open(ruta).convert("RGB")
    esc = max(ancho / im.width, alto / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS).crop((0, 0, ancho, alto))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def partir(texto, n):
    lineas, actual = [], ""
    for p in texto.split():
        if len(actual) + len(p) + 1 > n:
            lineas.append(actual)
            actual = p
        else:
            actual = (actual + " " + p).strip()
    return lineas + [actual]


def chip(x, y, texto, color=SUAVE, borde=BORDE, fondo=BARRA, t=17):
    ancho = len(texto) * t * 0.56 + 28
    return f'<rect x="{x}" y="{y}" width="{ancho:.0f}" height="{t+18}" rx="{(t+18)/2:.0f}" fill="{fondo}" stroke="{borde}" stroke-width="1.5"/><text x="{x+14}" y="{y+t+3}" font-size="{t}" fill="{color}">{escape(texto)}</text>', ancho


# ---------------------------------------------------------------- pixeles
LETRAS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
}


def pixeles(palabra, x0, y0, p, retraso=0.0, paso=0.018):
    """Letras de pixeles que se arman de izquierda a derecha."""
    blancos, azules, x, col = [], [], x0, 0
    for ch in palabra:
        if ch == "_":
            azules.append((x, y0 + 6 * p + p * 0.6, 5 * p, p * 0.9, retraso + col * paso))
        else:
            for fila, linea in enumerate(LETRAS[ch]):
                for c, v in enumerate(linea):
                    if v == "#":
                        blancos.append(f'<rect class="px" {d(retraso + (col + c) * paso + fila * 0.004)} x="{x + c*p}" y="{y0 + fila*p}" width="{p}" height="{p}"/>')
        x += 6 * p
        col += 6
    return "".join(blancos), azules


# ---------------------------------------------------------------- 1. portada
def banner():
    H, P = 480, 18
    ancho = 9 * 6 * P - P
    x0, y0 = (W - ancho) // 2, 150
    blancos, azules = pixeles("ABE_GAMA_", x0, y0, P, retraso=2.35)
    (ax, ay, aw, ah, ad), (cx, cy, cw, ch_, cd) = azules
    arranque = ["BIOS v1.0 — AbeGama.OS", "checking filesystem ............ [ OK ]", "loading projects [10] .......... [ OK ]",
                "mounting /dev/github ........... [ OK ]", "starting graphical shell ....... [ OK ]"]
    boot = "".join(f'<text class="ap" {d(0.2 + i*0.3)} x="{W//2-235}" y="{170 + i*30}" font-size="19" fill="{AZUL if i == 0 else SUAVE}">{escape(t)}</text>'
                   for i, t in enumerate(arranque))
    roles = ["apps móviles", "tiendas online", "paneles de administración", "sistemas a medida"]
    rotan = "".join(f'<text class="rol" style="animation-delay:{3.4 + i*2.6:.1f}s" x="612" y="408" font-size="26" fill="{AZUL}" font-weight="bold">{escape(r)}</text>'
                    for i, r in enumerate(roles))
    chips, x = "", 0
    datos = [("● disponible para proyectos", VERDE), ("Arequipa, Perú", SUAVE), ("DCG Triak", SUAVE), ("Flutter · Next.js · Supabase", SUAVE)]
    piezas = []
    for texto, color in datos:
        c, a = chip(0, 0, texto, color, t=16)
        piezas.append((c, a))
    total = sum(a for _, a in piezas) + 14 * (len(piezas) - 1)
    x = (W - total) / 2
    for i, (c, a) in enumerate(piezas):
        chips += f'<g transform="translate({x:.0f},432)"><g class="sube" {d(3.0 + i*0.12)}>{c}</g></g>'
        x += a + 14
    css = f'''
#boot{{animation:fuera .3s 2.1s forwards}}
@keyframes fuera{{to{{opacity:0}}}}
.rol{{opacity:0;animation:rol 10.4s infinite}}
@keyframes rol{{0%{{opacity:0;transform:translateY(14px)}}3%,22%{{opacity:1;transform:none}}25%,100%{{opacity:0;transform:translateY(-14px)}}}}
.scan{{animation:scan 7s linear 3s infinite;opacity:0}}
@keyframes scan{{0%{{transform:translateY(-140px);opacity:1}}100%{{transform:translateY({H}px);opacity:1}}}}
.subr{{transform:scaleX(0);transform-origin:{ax}px 0;transform-box:view-box;animation:subr .4s {ad:.2f}s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes subr{{to{{transform:scaleX(1)}}}}
'''
    cuerpo = f'''
<defs><linearGradient id="banda" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AZUL}" stop-opacity="0"/><stop offset=".5" stop-color="{AZUL}" stop-opacity=".07"/><stop offset="1" stop-color="{AZUL}" stop-opacity="0"/></linearGradient></defs>
<rect class="scan" x="0" y="0" width="{W}" height="140" fill="url(#banda)"/>
<text x="34" y="44" font-size="17" fill="{SUAVE}" letter-spacing="2">ABEGAMA.OS — V1.0</text>
<text x="300" y="44" font-size="17" fill="{AZUL}">◆ ACH 3/10</text>
<text x="{W-34}" y="44" font-size="17" fill="{SUAVE}" text-anchor="end" letter-spacing="2">SYSTEM READY <tspan fill="{AZUL}" class="pulso">● ONLINE</tspan></text>
<line x1="2" y1="66" x2="{W-2}" y2="66" stroke="{BORDE}" stroke-width="2"/>
<text x="34" y="108" font-size="17" fill="{TENUE}">&gt; ~ / abegama / github</text>
<text x="{W-34}" y="108" font-size="17" fill="{TENUE}" text-anchor="end">[ 2026 ]</text>
<g id="boot">{boot}</g>
<g fill="#f4f7fb">{blancos}</g>
<rect class="subr" x="{ax}" y="{ay:.0f}" width="{aw}" height="{ah:.0f}" fill="{AZUL}"/>
<rect class="ap" style="animation:ap .1s {cd:.2f}s forwards, parpadeo 1.1s steps(1) {cd+0.5:.2f}s infinite" x="{cx}" y="{cy:.0f}" width="{cw}" height="{ch_:.0f}" fill="{AZUL}"/>
<text class="ap" {d(3.0)} x="{W//2}" y="352" font-size="22" fill="{SUAVE}" text-anchor="middle">Desarrollador full-stack · apps y webs reales para negocios</text>
<text class="ap" {d(3.2)} x="600" y="408" font-size="26" fill="{TEXTO}" text-anchor="end">&gt; construyo</text>
{rotan}
{chips}'''
    guardar("banner.svg", svg(H, cuerpo, css))


# ---------------------------------------------------------------- 2. destacados
DESTACADOS = [
    dict(slug="safirox", n="01", nombre="Safirox", periodo="2026.09", estado=("● DEMO EN VIVO", VERDE),
         frase="Tienda online que se arma sola según el rubro del negocio: florería, repostería, perfumería, ropa o variados.",
         puntos=["5 rubros, cada uno con su catálogo y sus reglas", "Carrito, checkout por pasos y boleta en PNG",
                 "Pedido directo a WhatsApp · pago Yape / BCP", "Panel admin: productos, pedidos, sedes y stock"],
         stack=["Next.js 16", "React 19", "TypeScript", "Tailwind 4"], tipo="web",
         fotos=["capturas/safirox-flores.jpg", "capturas/safirox-perfumes.jpg", "capturas/safirox-reposteria.jpg"]),
    dict(slug="trimflow", n="02", nombre="TrimFlow", periodo="2026.05 → 2026.09", estado=("● TERMINADO", AZUL),
         frase="App para barberías con modo cliente y modo barbero en una sola app, para varias sedes.",
         puntos=["Reservas, agenda y calendario del barbero", "Multi-negocio con seguridad por fila (RLS)",
                 "Puntos y auditoría que no se puede editar", "Panel admin de servicios y productos"],
         stack=["Flutter", "BLoC", "Supabase", "Postgres"], tipo="celular", fotos=["Destacados", "AgendaBarbero", "PanelAdmin", "1Reserva"]),
    dict(slug="examora", n="03", nombre="Examora", periodo="2026.04 → 2026.08", estado=("● TERMINADO", AZUL),
         frase="App premium para que los docentes preparen los exámenes del MINEDU (Nombramiento y Ascenso).",
         puntos=["+6,000 preguntas reales con explicación", "Simulacros cronometrados como el examen",
                 "Repaso inteligente a los 1, 3 y 7 días", "Pago único premium validado en el servidor"],
         stack=["Flutter", "Clean Arch", "Supabase", "Offline"], tipo="celular", fotos=["2_inicio", "3_premium_beneficios", "5_cuenta", "1_bienvenida"]),
]


def pase(clase, n, T):
    """Keyframes de un pase de diapositivas: cada imagen se ve 1/n del ciclo."""
    tramo = 100 / n
    return f'''.{clase}{{opacity:0;animation:{clase} {T}s infinite}}
@keyframes {clase}{{0%{{opacity:0}}{tramo*0.08:.1f}%{{opacity:1}}{tramo*0.92:.1f}%{{opacity:1}}{tramo:.1f}%,100%{{opacity:0}}}}'''


def foto(slug, f):
    """Nombre de una captura del portafolio, o una ruta completa."""
    return os.path.join(AQUI, f) if f.startswith("capturas/") else os.path.join(FOTOS, slug, f + ".png")


def destacado(p):
    H = 610
    T = 3.2 * len(p["fotos"])
    left = 64
    lineas = partir(p["frase"], 44)
    frase = "".join(f'<text class="sube" {d(0.45 + i*0.08)} x="{left}" y="{250 + i*30}" font-size="21" fill="{SUAVE}">{escape(l)}</text>' for i, l in enumerate(lineas))
    y_p = 250 + len(lineas) * 30 + 26
    puntos = "".join(f'<text class="sube" {d(0.8 + i*0.18)} x="{left}" y="{y_p + i*34}" font-size="19" fill="{TEXTO}"><tspan fill="{AZUL}">▸</tspan> {escape(t)}</text>' for i, t in enumerate(p["puntos"]))
    chips, x = "", left
    for i, s in enumerate(p["stack"]):
        c, a = chip(0, 0, s, AZUL, "#1a3a66", "#0e1a2e", t=16)
        chips += f'<g transform="translate({x:.0f},{H-82})"><g class="sube" {d(1.6 + i*0.1)}>{c}</g></g>'
        x += a + 10
    css = pase("f", len(p["fotos"]), T) + '''
.flota{animation:flota 6s ease-in-out infinite}
@keyframes flota{50%{transform:translateY(-8px)}}
.brillo{animation:brillo 2.4s ease-in-out infinite}
@keyframes brillo{50%{opacity:.45}}'''
    imgs = ""
    if p["tipo"] == "web":
        bx, by, bw, bh = 628, 120, 520, 360
        for i, f in enumerate(p["fotos"]):
            imgs += f'<image class="f" style="animation-delay:{i*T/len(p["fotos"]) - T:.2f}s" x="{bx}" y="{by+34}" width="{bw}" height="{bh-34}" preserveAspectRatio="xMidYMin slice" clip-path="url(#pantalla)" href="{b64(foto(p["slug"], f), bw*2, (bh-34)*2)}"/>'
        equipo = f'''<g class="flota">
<rect x="{bx-8}" y="{by-8}" width="{bw+16}" height="{bh+16}" rx="18" fill="#04070d" stroke="{BORDE}" stroke-width="2"/>
<clipPath id="pantalla"><rect x="{bx}" y="{by+34}" width="{bw}" height="{bh-34}" rx="0"/></clipPath>
<rect x="{bx}" y="{by}" width="{bw}" height="34" rx="10" fill="{BARRA}"/>
<circle cx="{bx+20}" cy="{by+17}" r="5" fill="#ff5f57"/><circle cx="{bx+38}" cy="{by+17}" r="5" fill="#febc2e"/><circle cx="{bx+56}" cy="{by+17}" r="5" fill="#28c840"/>
<rect x="{bx+80}" y="{by+8}" width="{bw-110}" height="18" rx="9" fill="#0a0f1a"/>
<text x="{bx+96}" y="{by+22}" font-size="13" fill="{TENUE}">safirox-zeta.vercel.app</text>
{imgs}
</g>'''
    else:
        pw, ph = 212, 460
        fx, fy = 920, 86
        bx2 = 760
        for i, f in enumerate(p["fotos"]):
            imgs += f'<image class="f" style="animation-delay:{i*T/len(p["fotos"]) - T:.2f}s" x="{fx}" y="{fy}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMin slice" clip-path="url(#cel1)" href="{b64(foto(p["slug"], f), pw*2, ph*2)}"/>'
        atras = b64(foto(p["slug"], p["fotos"][1]), pw * 2, ph * 2)
        equipo = f'''<clipPath id="cel1"><rect x="{fx}" y="{fy}" width="{pw}" height="{ph}" rx="26"/></clipPath>
<clipPath id="cel2"><rect x="{bx2}" y="{fy+40}" width="{pw}" height="{ph}" rx="26"/></clipPath>
<g class="flota" style="animation-delay:-3s;opacity:.55">
<rect x="{bx2-9}" y="{fy+31}" width="{pw+18}" height="{ph+18}" rx="34" fill="#04070d" stroke="{BORDE}" stroke-width="2"/>
<image x="{bx2}" y="{fy+40}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMin slice" clip-path="url(#cel2)" href="{atras}"/>
</g>
<g class="flota">
<rect x="{fx-9}" y="{fy-9}" width="{pw+18}" height="{ph+18}" rx="34" fill="#04070d" stroke="{AZUL}" stroke-opacity=".5" stroke-width="2"/>
{imgs}
<rect x="{fx+pw/2-34}" y="{fy+8}" width="68" height="16" rx="8" fill="#04070d"/>
</g>'''
    estado, color = p["estado"]
    cuerpo = f'''{barra(f"~/proyectos/{p['slug']}", p["periodo"])}
<text class="ap" {d(0.1)} x="{left}" y="118" font-size="16" fill="{AZUL}" letter-spacing="3">PROYECTO NUEVO · {p["n"]}</text>
<g class="brillo"><rect x="{left+282}" y="98" width="78" height="28" rx="14" fill="#10213a" stroke="{AZUL}" stroke-width="1.5"/>
<text x="{left+321}" y="118" font-size="15" fill="{AZUL}" text-anchor="middle" font-weight="bold">NEW</text></g>
<text class="sube" {d(0.25)} x="{left-4}" y="196" font-size="64" fill="{TEXTO}" font-weight="bold">&gt; {escape(p["nombre"])}<tspan fill="{AZUL}" class="cursor">_</tspan></text>
{frase}
{puntos}
{chips}
<text class="ap" {d(2.0)} x="{left}" y="{H-104}" font-size="16" fill="{color}" letter-spacing="2"><tspan class="pulso">{estado.split(" ", 1)[0]}</tspan> {escape(estado.split(" ", 1)[1])}</text>
{equipo}'''
    guardar(f"nuevo-{p['slug']}.svg", svg(H, cuerpo, css))


# ---------------------------------------------------------------- 3. en construcción
def construccion():
    H = 360
    giro = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    tarjetas = ""
    datos = [("Triviom", "Gestión escolar para colegios: notas, asistencia y comunicación con las familias.", "Flutter · Next.js · Supabase", "2026.06 → …", 68),
             ("Zura", "App para descubrir la comida escondida de Arequipa: huariques, carretillas y reseñas.", "React Native · Expo · Supabase", "2026.07 → …", 41)]
    css = f'''.giro{{opacity:0;animation:giro 1s steps(1) infinite}}
@keyframes giro{{0%{{opacity:1}}10%,100%{{opacity:0}}}}
.prog{{transform:scaleX(0);transform-box:fill-box;transform-origin:left;animation:prog 5s cubic-bezier(.4,0,.2,1) infinite}}
@keyframes prog{{0%{{transform:scaleX(0)}}60%,85%{{transform:scaleX(1)}}100%{{transform:scaleX(1);opacity:0}}}}
.luz{{animation:luz 2.2s linear infinite}}
@keyframes luz{{from{{transform:translateX(-120px)}}to{{transform:translateX(520px)}}}}'''
    for i, (nombre, frase, stack, periodo, pct) in enumerate(datos):
        x = 40 + i * 570
        sp = "".join(f'<text class="giro" style="animation-delay:{k/10:.1f}s" x="{x+28}" y="136" font-size="24" fill="{AMBAR}">{c}</text>' for k, c in enumerate(giro))
        lineas = "".join(f'<text x="{x+28}" y="{180 + j*27}" font-size="18" fill="{SUAVE}">{escape(l)}</text>' for j, l in enumerate(partir(frase, 50)))
        largo = 494
        tarjetas += f'''<g class="sube" {d(0.2 + i*0.2)}>
<rect x="{x}" y="88" width="550" height="240" rx="14" fill="{VENT}" stroke="{BORDE}" stroke-width="2"/>
{sp}<text x="{x+62}" y="136" font-size="30" fill="{TEXTO}" font-weight="bold">{nombre}</text>
<text x="{x+522}" y="132" font-size="15" fill="{TENUE}" text-anchor="end">{periodo}</text>
{lineas}
<text x="{x+28}" y="252" font-size="16" fill="{AZUL}">{escape(stack)}</text>
<rect x="{x+28}" y="274" width="{largo}" height="12" rx="6" fill="{BARRA}" stroke="{BORDE}"/>
<clipPath id="barra{i}"><rect x="{x+28}" y="274" width="{largo*pct/100:.0f}" height="12" rx="6"/></clipPath>
<g clip-path="url(#barra{i})"><rect class="prog" style="animation-delay:{i*0.6}s" x="{x+28}" y="274" width="{largo*pct/100:.0f}" height="12" fill="{AMBAR}"/>
<rect class="luz" x="{x+28}" y="274" width="80" height="12" fill="#fff" opacity=".25"/></g>
<text x="{x+522}" y="310" font-size="15" fill="{AMBAR}" text-anchor="end">compilando… {pct}%</text>
</g>'''
    cuerpo = f'''{barra("~/en-construcción — flutter run --watch", "2 proyectos")}
{tarjetas}'''
    guardar("construccion.svg", svg(H, cuerpo, css))


# ---------------------------------------------------------------- 4. más proyectos (ls -la)
def otros():
    filas = [("perfumeria-original", "2026.09", "Next.js", "demo", "tienda + panel, 3 sedes"),
             ("calma-peru", "2026.08→09", "WordPress", "en vivo", "certificados automáticos"),
             ("fadex-sac", "2026.01→03", "Flutter Web", "en vivo", "web corporativa + panel"),
             ("abidetalles", "2025.11→01", "Flutter Web", "en vivo", "tienda de florería"),
             ("safecheck", "2025.04→07", "Flutter", "terminado", "QR, GPS y alertas en obra")]
    H = 120 + len(filas) * 44 + 40
    cols = [40, 190, 470, 610, 770, 900]
    cab = ["permisos", "nombre", "fecha", "stack", "estado", "qué es"]
    cuerpo = barra("~/proyectos — ls -la --sort=time", f"{len(filas)} más")
    cuerpo += f'<text class="ap" x="40" y="104" font-size="18" fill="{AZUL}">$ <tspan fill="{TEXTO}">ls -la ~/proyectos/otros</tspan></text>'
    for i, t in enumerate(cab):
        cuerpo += f'<text class="ap" {d(0.3)} x="{cols[i]}" y="140" font-size="14" fill="{TENUE}" letter-spacing="1.5">{t.upper()}</text>'
    for k, (n, f, s, e, q) in enumerate(filas):
        y = 180 + k * 44
        col_e = VERDE if e == "en vivo" else (AMBAR if e == "demo" else AZUL)
        cuerpo += f'''<g class="sube" {d(0.5 + k*0.14)}>
<rect x="28" y="{y-28}" width="{W-56}" height="38" rx="8" fill="{BARRA}" opacity="{.55 if k % 2 == 0 else 0}"/>
<text x="{cols[0]}" y="{y}" font-size="17" fill="{TENUE}">drwxr-xr-x</text>
<text x="{cols[1]}" y="{y}" font-size="17" fill="{TEXTO}" font-weight="bold">{n}/</text>
<text x="{cols[2]}" y="{y}" font-size="17" fill="{SUAVE}">{f}</text>
<text x="{cols[3]}" y="{y}" font-size="17" fill="{AZUL}">{s}</text>
<text x="{cols[4]}" y="{y}" font-size="17" fill="{col_e}">● {e}</text>
<text x="{cols[5]}" y="{y}" font-size="17" fill="{SUAVE}">{escape(q)}</text></g>'''
    guardar("otros.svg", svg(H, cuerpo))


# ---------------------------------------------------------------- 5. neofetch
def neofetch():
    H = 500
    # avatar como el del portafolio: bloque azul, ventana negra y "AG" en pixeles
    ax, ay, s = 64, 104, 300
    p = 13
    ag_ancho = 11 * p
    ag, _ = pixeles("AG", ax + (s - ag_ancho) // 2, ay + 100, p, retraso=0.3, paso=0.03)
    avatar = f'''<rect x="{ax}" y="{ay}" width="{s}" height="{s}" fill="#000"/>
<rect x="{ax+24}" y="{ay+24}" width="{s-48}" height="{s-48}" fill="{AZUL}"/>
<rect x="{ax+24}" y="{ay+24}" width="32" height="32" fill="#fff" opacity=".35"/>
<rect x="{ax+s-56}" y="{ay+s-56}" width="32" height="32" fill="#000" opacity=".45"/>
<rect x="{ax+52}" y="{ay+52}" width="{s-104}" height="{s-104}" fill="#000"/>
<g fill="{AZUL}">{ag}</g>
<rect x="{ax+s/2-5}" y="{ay+s-84}" width="10" height="10" fill="{AZUL}" class="pulso"/>'''
    campos = [("OS", "AbeGama.OS v1.0 — Arequipa, Perú"), ("Rol", "Full-stack developer · DCG Triak"),
              ("Móvil", "Flutter · Dart · BLoC · get_it + injectable"), ("Web", "Next.js · React · TypeScript · Tailwind"),
              ("Backend", "Supabase (Postgres · RLS · Edge Functions) · Firebase"), ("Arquitectura", "Clean Architecture · feature-first"),
              ("Pruebas", "flutter_test · bloc_test · mocktail"), ("Deploy", "GitHub Actions · Vercel · Firebase Hosting"),
              ("Repos", "24 · el código de clientes es privado")]
    x = 420
    cuerpo = barra("~ — neofetch", "zsh")
    cuerpo += avatar
    cuerpo += f'<text class="ap" {d(0.2)} x="{x}" y="118" font-size="22" font-weight="bold"><tspan fill="{AZUL}">adrian</tspan><tspan fill="{TEXTO}">@</tspan><tspan fill="{AZUL}">abegama</tspan></text>'
    cuerpo += f'<rect class="ap" {d(0.3)} x="{x}" y="130" width="250" height="2" fill="{BORDE}"/>'
    for i, (k, v) in enumerate(campos):
        cuerpo += f'<text class="sube" {d(0.45 + i*0.15)} x="{x}" y="{168 + i*30}" font-size="18"><tspan fill="{AZUL}" font-weight="bold">{k}</tspan><tspan fill="{TENUE}">: </tspan><tspan fill="{TEXTO}">{escape(v)}</tspan></text>'
    colores = ["#0b111d", "#ff5f57", "#28c840", "#febc2e", AZUL, "#c084fc", "#22d3ee", TEXTO]
    yb = 168 + len(campos) * 30 + 6
    for i, c in enumerate(colores):
        cuerpo += f'<rect class="ap" {d(0.45 + len(campos)*0.15 + i*0.05)} x="{x + i*42}" y="{yb}" width="42" height="22" fill="{c}"/>'
    guardar("neofetch.svg", svg(H, cuerpo))


# ---------------------------------------------------------------- 6. cómo construyo (arquitectura)
def arquitectura():
    H = 470

    def caja(x, y, w, h, titulo, sub, color=AZUL, retraso=0):
        lineas = "".join(f'<text x="{x+w/2}" y="{y+62 + i*22}" font-size="15" fill="{SUAVE}" text-anchor="middle">{escape(t)}</text>' for i, t in enumerate(sub))
        return f'''<g class="sube" {d(retraso)}><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{VENT}" stroke="{color}" stroke-opacity=".7" stroke-width="2"/>
<text x="{x+w/2}" y="{y+36}" font-size="20" fill="{TEXTO}" font-weight="bold" text-anchor="middle">{escape(titulo)}</text>{lineas}</g>'''

    def linea(id_, d_, color, dur, retraso):
        return f'''<path id="{id_}" d="{d_}" fill="none" stroke="{BORDE}" stroke-width="2" stroke-dasharray="6 6"/>
<circle r="5" fill="{color}"><animateMotion dur="{dur}s" begin="{retraso}s" repeatCount="indefinite" rotate="auto"><mpath href="#{id_}"/></animateMotion></circle>
<circle r="5" fill="{color}" opacity=".5"><animateMotion dur="{dur}s" begin="{retraso + dur/2:.2f}s" repeatCount="indefinite"><mpath href="#{id_}"/></animateMotion></circle>'''

    cuerpo = barra("~/como-construyo.md", "arquitectura")
    cuerpo += f'<text class="ap" x="40" y="106" font-size="18" fill="{AZUL}">$ <tspan fill="{TEXTO}">cat como-construyo.md</tspan></text>'
    cuerpo += linea("l1", "M 280 190 C 380 190, 380 260, 470 260", AZUL, 2.4, 0.8)
    cuerpo += linea("l2", "M 280 330 C 380 330, 380 270, 470 270", AZUL, 2.4, 1.2)
    cuerpo += linea("l3", "M 730 265 L 860 265", VERDE, 1.8, 1.0)
    cuerpo += linea("l4", "M 600 380 L 600 340", AMBAR, 1.4, 1.4)
    cuerpo += caja(60, 140, 220, 100, "App móvil", ["Flutter · BLoC", "Clean Architecture"], AZUL, 0.2)
    cuerpo += caja(60, 280, 220, 100, "Web / Panel", ["Next.js · React", "TypeScript"], AZUL, 0.35)
    cuerpo += caja(470, 190, 260, 150, "Supabase", ["Auth · Storage", "Edge Functions", "RLS por negocio"], VERDE, 0.5)
    cuerpo += caja(860, 210, 280, 110, "Postgres", ["vistas para lo calculado", "funciones privadas"], VERDE, 0.65)
    cuerpo += f'<g class="sube" {d(0.8)}><rect x="470" y="380" width="260" height="46" rx="10" fill="{BARRA}" stroke="{AMBAR}" stroke-opacity=".6" stroke-width="1.5"/><text x="600" y="409" font-size="16" fill="{AMBAR}" text-anchor="middle">CI/CD · GitHub Actions</text></g>'
    notas = ["cada negocio ve solo lo suyo (RLS)", "lo calculado va en vistas, no en tablas", "permisos separados: leer / escribir"]
    for i, n in enumerate(notas):
        cuerpo += f'<text class="ap" {d(1.2 + i*0.2)} x="780" y="{372 + i*26}" font-size="15" fill="{TENUE}"># {escape(n)}</text>'
    guardar("arquitectura.svg", svg(H, cuerpo))


# ---------------------------------------------------------------- 9. minijuego: Bug Invaders
SPRITES = {
    "pulpo": (["...##...", "..####..", ".######.", "##.##.##", "########", "..#..#..", ".#.##.#.", "#.#..#.#"],
              ["...##...", "..####..", ".######.", "##.##.##", "########", ".#.##.#.", "#......#", ".#....#."]),
    "cangrejo": (["..#.....#..", "...#...#...", "..#######..", ".##.###.##.", "###########", "#.#######.#", "#.#.....#.#", "...##.##..."],
                 ["..#.....#..", "#..#...#..#", "#.#######.#", "###.###.###", "###########", ".#########.", "..#.....#..", ".#.......#."]),
    "nave": (["......#......", ".....###.....", ".....###.....", ".###########.", "#############", "#############", "#############", "#############"],),
    "boom": (["....#...#....", ".#...#.#...#.", "..#.......#..", "...#.....#...", "##.........##", "...#.....#...", "..#.......#..", ".#...#.#...#.", "....#...#...."],),
}


def sprite(nombre, x, y, p, frame=0):
    filas = SPRITES[nombre][frame]
    return "".join(f'<rect x="{x + c*p}" y="{y + f*p}" width="{p}" height="{p}"/>'
                   for f, linea in enumerate(filas) for c, v in enumerate(linea) if v == "#")


def invasores():
    """Un Space Invaders que se juega solo: la nave elimina los bugs y las pruebas aguantan los disparos."""
    H, T, PASO = 500, 16.0, 0.4
    pct = lambda t: f"{t / T * 100:.2f}%"
    # la formación se mueve a saltos, como el arcade: 12 px cada 0,4 s, ida y vuelta
    ida = [12 * i for i in range(6)] + [12 * i for i in range(4, -6, -1)] + [12 * i for i in range(-4, 0)]
    pasos = (ida * 3)[: int(T / PASO)]
    f = lambda t: pasos[int(t / PASO) % len(pasos)]
    filas = [("pulpo", 6, 150, "#ff5d8f", 30, ["null", "undefined", "NaN", "404", "500", "CORS", "typo"]),
             ("cangrejo", 5, 236, AMBAR, 20, ["race", "leak", "loop∞", "merge", "regex", "IE11", "deadline"])]
    cols = [240 + i * 120 for i in range(7)]
    nave_y, nave_p = 410, 5
    css, cuerpo = [], []
    n = 0

    def anim(keyframes, extra=""):
        nonlocal n
        n += 1
        css.append(f".a{n}{{animation:a{n} {T}s linear infinite;{extra}}}@keyframes a{n}{{{keyframes}}}")
        return f"a{n}"

    # orden de los disparos (fijo) y momentos en que cae cada bug
    objetivos = [(r, c) for r in range(2) for c in range(7)]
    orden = [objetivos[i] for i in (10, 3, 12, 6, 0, 8, 13, 4, 1, 11, 7, 2, 9, 5)]
    golpes = {}
    for k, (r, c) in enumerate(orden):
        golpes[(r, c)] = 1.0 + 0.8 * k

    # formación
    formacion = []
    for r, (tipo, p, y, color, pts, nombres) in enumerate(filas):
        ancho = len(SPRITES[tipo][0][0]) * p
        for c, x in enumerate(cols):
            th = golpes[(r, c)]
            x0 = x - ancho / 2
            vivo = anim(f"0%{{opacity:0}}3%{{opacity:1}}{pct(th)}{{opacity:1}}{pct(th + 0.02)},100%{{opacity:0}}")
            a = anim("0%{opacity:1}50%{opacity:0}", "animation-duration:1s;animation-timing-function:steps(1)")
            b = anim("0%{opacity:0}50%{opacity:1}", "animation-duration:1s;animation-timing-function:steps(1)")
            boom = anim(f"0%,{pct(th)}{{opacity:0}}{pct(th + 0.02)},{pct(th + 0.3)}{{opacity:1}}{pct(th + 0.34)},100%{{opacity:0}}")
            mas = anim(f"0%,{pct(th)}{{opacity:0;transform:translateY(0)}}{pct(th + 0.05)}{{opacity:1}}{pct(th + 0.7)}{{opacity:0;transform:translateY(-26px)}}100%{{opacity:0}}")
            formacion.append(f'''<g class="{vivo}" fill="{color}"><g class="{a}">{sprite(tipo, x0, y, p, 0)}</g><g class="{b}" style="opacity:0">{sprite(tipo, x0, y, p, 1)}</g>
<text x="{x}" y="{y + 64}" font-size="14" fill="{color}" opacity=".75" text-anchor="middle">{escape(nombres[c])}</text></g>
<g class="{boom}" style="opacity:0" fill="{AMBAR}">{sprite("boom", x - 26, y, 4)}</g>
<text class="{mas}" style="opacity:0" x="{x}" y="{y - 6}" font-size="16" fill="{TEXTO}" text-anchor="middle" font-weight="bold">+{pts}</text>''')
    valores = ";".join(f"{v} 0" for v in pasos)
    cuerpo.append(f'<g>{"".join(formacion)}<animateTransform attributeName="transform" type="translate" calcMode="discrete" dur="{T}s" repeatCount="indefinite" values="{valores}"/></g>')

    # disparos de la nave y su recorrido
    marcos, puntos, x_ant = [], 0, 600
    nave_w = 13 * nave_p
    for k, (r, c) in enumerate(orden):
        th = golpes[(r, c)]
        y_obj = filas[r][2] + 20
        vuelo = (nave_y - y_obj) / 1100
        tf = th - vuelo
        x = cols[c] + f(th)
        marcos += [(tf - 0.12, x), (tf + 0.04, x)]
        laser = anim(f"0%,{pct(tf)}{{opacity:0;transform:translateY(0)}}{pct(tf + 0.01)}{{opacity:1;transform:translateY(0)}}"
                     f"{pct(th)}{{opacity:1;transform:translateY({y_obj - nave_y}px)}}{pct(th + 0.01)},100%{{opacity:0;transform:translateY({y_obj - nave_y}px)}}")
        cuerpo.append(f'<rect class="{laser}" style="opacity:0" x="{x - 2}" y="{nave_y - 18}" width="4" height="18" rx="2" fill="{AZUL}"/>')
    pasos_nave = [(0, 600)] + marcos + [(12.6, 600), (T, 600)]
    kf = "".join(f"{pct(t)}{{transform:translateX({x - nave_w/2:.0f}px)}}" for t, x in pasos_nave)
    nave = anim(kf, "animation-timing-function:ease-in-out")
    cuerpo.append(f'<g class="{nave}" fill="{AZUL}">{sprite("nave", 0, nave_y, nave_p)}<rect x="{nave_w/2 - 1}" y="{nave_y + 44}" width="2" height="6" fill="{AZUL}" opacity=".5"/></g>')

    # barreras: las pruebas atajan los disparos de los bugs
    for i, (bx, nombre) in enumerate([(300, "tests"), (600, "CI"), (900, "review")]):
        bloque = ["..######..", ".########.", "##########", "##########", "###....###", "##......##"]
        cuerpo.append(f'<g fill="{VERDE}" opacity=".85">{sprite_libre(bloque, bx - 40, 340, 8)}</g>'
                      f'<text x="{bx}" y="406" font-size="14" fill="{VERDE}" text-anchor="middle">{nombre}</text>')
    for t0, bx in [(3.1, 300), (6.5, 900), (9.7, 600)]:
        cae = anim(f"0%,{pct(t0)}{{opacity:0;transform:translateY(0)}}{pct(t0 + 0.01)}{{opacity:1}}{pct(t0 + 0.55)}{{opacity:1;transform:translateY(62px)}}{pct(t0 + 0.56)},100%{{opacity:0;transform:translateY(62px)}}")
        chispa = anim(f"0%,{pct(t0 + 0.55)}{{opacity:0}}{pct(t0 + 0.57)},{pct(t0 + 0.8)}{{opacity:1}}{pct(t0 + 0.85)},100%{{opacity:0}}")
        cuerpo.append(f'<path class="{cae}" style="opacity:0" d="M{bx} 272l4 6-4 6 4 6-4 6" fill="none" stroke="#ff5d8f" stroke-width="3"/>'
                      f'<text class="{chispa}" style="opacity:0" x="{bx}" y="336" font-size="14" fill="{VERDE}" text-anchor="middle" font-weight="bold">BLOCKED</text>')

    # marcador: cambia en cada bug eliminado
    momentos = [0.0] + [golpes[o] for o in orden] + [T]
    for k in range(len(momentos) - 1):
        if k:
            r, _ = orden[k - 1]
            puntos += filas[r][4]
        t0, t1 = momentos[k], momentos[k + 1]
        vis = anim(f"0%,{pct(t0)}{{opacity:0}}{pct(t0 + 0.001)},{pct(t1)}{{opacity:1}}{pct(t1 + 0.001)},100%{{opacity:0}}" if k else
                   f"0%,{pct(t1)}{{opacity:1}}{pct(t1 + 0.001)},100%{{opacity:0}}")
        cuerpo.append(f'<text class="{vis}" x="60" y="118" font-size="20" fill="{TEXTO}">SCORE <tspan fill="{AZUL}">{puntos:06d}</tspan></text>')
    fin = anim(f"0%,{pct(12.2)}{{opacity:0;transform:scale(.9)}}{pct(12.5)},{pct(15.4)}{{opacity:1;transform:none}}{pct(15.8)},100%{{opacity:0}}",
               "transform-origin:600px 300px")
    cuerpo.append(f'''<g class="{fin}" style="opacity:0">
<text x="600" y="288" font-size="40" fill="{TEXTO}" text-anchor="middle" font-weight="bold" letter-spacing="6">WAVE CLEARED</text>
<text x="600" y="322" font-size="20" fill="{VERDE}" text-anchor="middle">0 bugs en producción · deploy ✓</text></g>''')
    hud = f'''{barra("~/bug-invaders — npm run fix", "1UP")}
<text x="600" y="118" font-size="22" fill="{AMBAR}" text-anchor="middle" font-weight="bold" letter-spacing="8">BUG INVADERS</text>
<text x="{W-60}" y="118" font-size="20" fill="{TEXTO}" text-anchor="end">HI <tspan fill="{AZUL}">009999</tspan></text>
<line x1="40" y1="{H-30}" x2="{W-40}" y2="{H-30}" stroke="{VERDE}" stroke-opacity=".4" stroke-width="2"/>
<text x="60" y="{H-44}" font-size="14" fill="{TENUE}">VIDAS <tspan fill="{AZUL}">▲ ▲ ▲</tspan></text>
<text x="{W-60}" y="{H-44}" font-size="14" fill="{AMBAR}" text-anchor="end" class="cursor">INSERT COIN</text>'''
    guardar("bug-invaders.svg", svg(H, hud + "".join(cuerpo), "\n".join(css)))


# ---------------------------------------------------------------- 10. minijuego: python.exe (snake)
def serpiente():
    """Snake que se juega solo: busca cada símbolo de código por el camino más corto (BFS) y crece."""
    import random
    from collections import deque

    H, COLS, FILAS, CELDA, DT = 500, 34, 11, 28, 0.11
    x0, y0 = (W - COLS * CELDA) // 2, 128
    fichas = [";", "{}", "=>", "()", "[]", "</>", "&&", "++", "#", "λ"]
    azar = random.Random(7)
    cuerpo_s = deque([(4 - i, 5) for i in range(4)])  # la cabeza va primero
    crecer, cuadros, comidas = 0, [], []

    def nueva_comida():
        libres = [(c, f) for c in range(COLS) for f in range(FILAS) if (c, f) not in cuerpo_s]
        return azar.choice(libres)

    def camino(meta):
        ocupado = set(list(cuerpo_s)[:-1])
        cola, previo = deque([cuerpo_s[0]]), {cuerpo_s[0]: None}
        while cola:
            actual = cola.popleft()
            if actual == meta:
                break
            for dc, df in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                sig = (actual[0] + dc, actual[1] + df)
                if 0 <= sig[0] < COLS and 0 <= sig[1] < FILAS and sig not in ocupado and sig not in previo:
                    previo[sig] = actual
                    cola.append(sig)
        if meta not in previo:
            return None
        paso = meta
        while previo[paso] != cuerpo_s[0]:
            paso = previo[paso]
        return paso

    comida, aparece = nueva_comida(), 0
    while len(comidas) < len(fichas):
        cuadros.append(list(cuerpo_s))
        sig = camino(comida)
        if sig is None:  # sin camino: cualquier casilla libre al lado
            c, f = cuerpo_s[0]
            libres = [(c + a, f + b) for a, b in ((1, 0), (0, 1), (-1, 0), (0, -1))
                      if 0 <= c + a < COLS and 0 <= f + b < FILAS and (c + a, f + b) not in cuerpo_s]
            sig = libres[0]
        cuerpo_s.appendleft(sig)
        if crecer:
            crecer -= 1
        else:
            cuerpo_s.pop()
        if sig == comida:
            comidas.append((comida, aparece, len(cuadros)))
            crecer += 2
            if len(comidas) < len(fichas):
                comida, aparece = nueva_comida(), len(cuadros)
    cuadros.append(list(cuerpo_s))
    N = len(cuadros)
    T = N * DT + 2.6
    pct = lambda t: f"{t / T * 100:.3f}%"
    xy = lambda c, f: (x0 + c * CELDA, y0 + f * CELDA)
    css, partes, n = [], [], 0

    def anim(kf, extra="animation-timing-function:step-end"):
        nonlocal n
        n += 1
        css.append(f".s{n}{{animation:s{n} {T:.2f}s linear infinite;{extra}}}@keyframes s{n}{{{kf}}}")
        return f"s{n}"

    # tablero
    partes.append("".join(f'<rect x="{xy(c, f)[0]+2}" y="{xy(c, f)[1]+2}" width="{CELDA-4}" height="{CELDA-4}" rx="5" fill="#0d1524"/>'
                          for c in range(COLS) for f in range(FILAS)))
    # cuerpo: cada casilla se prende mientras la serpiente pasa por ella
    tramos = {}
    for t, s in enumerate(cuadros):
        for celda in s[1:]:
            tramos.setdefault(celda, []).append(t)
    for celda, ticks in tramos.items():
        kf, inicio, prev = ["0%{opacity:0}"], ticks[0], ticks[0]
        for t in ticks[1:] + [None]:
            if t is None or t != prev + 1:
                kf.append(f"{pct(inicio * DT)}{{opacity:1}}{pct((prev + 1) * DT)}{{opacity:0}}")
                inicio = t
            prev = t if t is not None else prev
        kf.append("100%{opacity:0}")
        x, y = xy(*celda)
        partes.append(f'<rect class="{anim("".join(kf))}" style="opacity:0" x="{x+3}" y="{y+3}" width="{CELDA-6}" height="{CELDA-6}" rx="6" fill="{AZUL}"/>')
    # cabeza
    kf = "".join(f"{pct(t * DT)}{{transform:translate({xy(*s[0])[0]}px,{xy(*s[0])[1]}px);opacity:1}}" for t, s in enumerate(cuadros))
    kf += f"{pct(N * DT)},100%{{opacity:0}}"
    partes.append(f'<g class="{anim(kf)}"><rect x="2" y="2" width="{CELDA-4}" height="{CELDA-4}" rx="7" fill="{TEXTO}"/>'
                  f'<rect x="{CELDA/2-6}" y="{CELDA/2-4}" width="4" height="4" fill="{FONDO}"/><rect x="{CELDA/2+2}" y="{CELDA/2-4}" width="4" height="4" fill="{FONDO}"/></g>')
    # comida y "+2"
    for i, ((c, f), t0, t1) in enumerate(comidas):
        x, y = xy(c, f)
        vis = anim(f"0%{{opacity:0}}{pct(t0 * DT)}{{opacity:1}}{pct(t1 * DT)}{{opacity:0}}100%{{opacity:0}}")
        sube = anim(f"0%,{pct(t1 * DT)}{{opacity:0;transform:translateY(0)}}{pct(t1 * DT + 0.05)}{{opacity:1}}{pct(t1 * DT + 0.7)}{{opacity:0;transform:translateY(-22px)}}100%{{opacity:0}}",
                    "animation-timing-function:ease-out")
        partes.append(f'''<g class="{vis}" style="opacity:0"><rect class="pulso" x="{x+1}" y="{y+1}" width="{CELDA-2}" height="{CELDA-2}" rx="7" fill="#2a1a08" stroke="{AMBAR}" stroke-width="1.5"/>
<text x="{x + CELDA/2}" y="{y + CELDA/2 + 5}" font-size="{15 if len(fichas[i]) < 3 else 12}" fill="{AMBAR}" text-anchor="middle" font-weight="bold">{escape(fichas[i])}</text></g>
<text class="{sube}" style="opacity:0" x="{x + CELDA/2}" y="{y - 4}" font-size="15" fill="{TEXTO}" text-anchor="middle" font-weight="bold">+2</text>''')
    # marcador
    cortes = [0] + [t1 for _, _, t1 in comidas] + [None]
    for k in range(len(cortes) - 1):
        t0, t1 = cortes[k] * DT, (cortes[k + 1] * DT if cortes[k + 1] is not None else T)
        kf = (f"0%{{opacity:0}}{pct(t0)}{{opacity:1}}{pct(t1)}{{opacity:0}}100%{{opacity:0}}" if k else f"0%{{opacity:1}}{pct(t1)}{{opacity:0}}100%{{opacity:0}}")
        oculto = ' style="opacity:0"' if k else ""
        partes.append(f'<text class="{anim(kf)}"{oculto} x="60" y="106" font-size="20" fill="{TEXTO}">TOKENS <tspan fill="{AMBAR}">{k:02d}/{len(fichas)}</tspan>  <tspan fill="{TENUE}">·</tspan>  LARGO <tspan fill="{AZUL}">{4 + 2*k:02d}</tspan></text>')
    fin = anim(f"0%,{pct(N * DT)}{{opacity:0;transform:scale(.92)}}{pct(N * DT + 0.25)},{pct(T - 0.35)}{{opacity:1;transform:none}}{pct(T - 0.05)},100%{{opacity:0}}",
               "animation-timing-function:ease-out;transform-origin:600px 282px")
    partes.append(f'''<g class="{fin}" style="opacity:0"><rect x="330" y="222" width="540" height="120" rx="14" fill="{FONDO}" fill-opacity=".92" stroke="{VERDE}" stroke-width="2"/>
<text x="600" y="276" font-size="32" fill="{VERDE}" text-anchor="middle" font-weight="bold" letter-spacing="4">BUILD SUCCESSFUL</text>
<text x="600" y="312" font-size="18" fill="{SUAVE}" text-anchor="middle">{len(fichas)} tokens · 0 errores · compilado en {N*DT:.1f}s</text></g>''')
    hud = f'''{barra("~/python.exe — la única serpiente que sé domar", "snake")}
<text x="{W-60}" y="106" font-size="20" fill="{AMBAR}" text-anchor="end" font-weight="bold" letter-spacing="6">PYTHON.EXE</text>
<text x="60" y="{H-26}" font-size="14" fill="{TENUE}"># busca cada símbolo por el camino más corto (BFS) · generado con Python</text>'''
    guardar("python-exe.svg", svg(H, hud + "".join(partes), "\n".join(css)))


# ---------------------------------------------------------------- 11. cierre
def cierre():
    H = 300
    lineas = [
        (f'<tspan fill="{AZUL}">$</tspan> <tspan fill="{TEXTO}">./contratar.sh --dev adrian</tspan>', 0.3),
        (f'<tspan fill="{SUAVE}">&gt; conectando con adrian@abegama ......</tspan> <tspan fill="{VERDE}">[ OK ]</tspan>', 1.1),
        (f'<tspan fill="{SUAVE}">&gt; estado</tspan><tspan x="230" fill="{VERDE}">● disponible para proyectos</tspan>', 1.6),
        (f'<tspan fill="{SUAVE}">&gt; hago</tspan><tspan x="230" fill="{TEXTO}">apps · tiendas online · paneles · sistemas a medida</tspan>', 2.0),
        (f'<tspan fill="{SUAVE}">&gt; portafolio</tspan><tspan x="230" fill="{AZUL}" text-decoration="underline">portafoliogama.vercel.app</tspan>', 2.4),
    ]
    cuerpo = barra("~ — zsh", "DCG Triak · Arequipa, Perú")
    for i, (t, dl) in enumerate(lineas):
        cuerpo += f'<text class="ap" {d(dl)} x="48" y="{110 + i*36}" font-size="21">{t}</text>'
    cuerpo += f'<rect class="ap" style="animation:ap .1s 2.8s forwards, parpadeo 1.1s steps(1) 2.9s infinite" x="48" y="{110 + len(lineas)*36 - 18}" width="12" height="22" fill="{AZUL}"/>'
    guardar("cierre.svg", svg(H, cuerpo))


def sprite_libre(filas, x, y, p):
    return "".join(f'<rect x="{x + c*p}" y="{y + f*p}" width="{p}" height="{p}"/>'
                   for f, linea in enumerate(filas) for c, v in enumerate(linea) if v == "#")


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    invasores()
    banner()
    for p in DESTACADOS:
        destacado(p)
    construccion()
    otros()
    neofetch()
    arquitectura()
    serpiente()
    cierre()
