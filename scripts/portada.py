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


# ---------------------------------------------------------------- 7. memes (rotan en una sola ventana)
def memes():
    H, T = 420, 21.0
    escenas = 3
    tramo = T / escenas

    def kf(nombre, inicio, fin):
        a, b = inicio / T * 100, fin / T * 100
        return f'@keyframes {nombre}{{0%,{a:.2f}%{{opacity:0;transform:translateY(10px)}}{a+1.2:.2f}%,{b-1.2:.2f}%{{opacity:1;transform:none}}{b:.2f}%,100%{{opacity:0}}}}'

    css, cuerpo, n = [], [], 0

    def el(texto_svg, inicio, fin):
        nonlocal n
        n += 1
        css.append(f'.m{n}{{opacity:0;animation:m{n} {T}s infinite}}' + kf(f"m{n}", inicio, fin))
        return f'<g class="m{n}">{texto_svg}</g>'

    # escena 1: git log
    ini, fin = 0, tramo
    cuerpo.append(el(f'<text x="50" y="118" font-size="20" fill="{AZUL}">$ <tspan fill="{TEXTO}">git log --oneline</tspan></text>', ini + .2, fin))
    commits = [("a1f3c2e", "arreglo final"), ("b7d9e01", "arreglo final (ahora sí)"), ("c4e8a77", "arreglo final final"),
               ("d2b6f19", "ok, este es el bueno"), ("e9a0c3d", "por favor funciona"), ("f00d4e2", "funciona. NO TOCAR")]
    for i, (h, m) in enumerate(commits):
        cuerpo.append(el(f'<text x="50" y="{160 + i*36}" font-size="20"><tspan fill="{AMBAR}">{h}</tspan>  <tspan fill="{TEXTO}">{escape(m)}</tspan></text>', ini + .8 + i * .5, fin))
    # escena 2: logros
    ini, fin = tramo, 2 * tramo

    def logro(y, titulo, detalle, num):
        return f'''<rect x="150" y="{y}" width="900" height="110" rx="14" fill="{BARRA}" stroke="{AZUL}" stroke-width="1.5"/>
<rect x="176" y="{y+25}" width="60" height="60" rx="12" fill="#10213a" stroke="{AZUL}" stroke-width="1.5"/>
<path d="M195 {y+41}h22v10a11 11 0 0 1-22 0zM195 {y+45}h-6a5 5 0 0 0 6 8M217 {y+45}h6a5 5 0 0 1-6 8M206 {y+62}v7M198 {y+72}h16" fill="none" stroke="{AMBAR}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<text x="262" y="{y+40}" font-size="15" fill="{AZUL}" letter-spacing="3">★ LOGRO DESBLOQUEADO · ACH {num}/10</text>
<text x="262" y="{y+72}" font-size="24" fill="{TEXTO}" font-weight="bold">{escape(titulo)}</text>
<text x="262" y="{y+96}" font-size="16" fill="{SUAVE}">{escape(detalle)}</text>'''

    cuerpo.append(el(logro(110, "Funciona en mi máquina", "Raro: el 99% de los devs ya lo tiene.", 3), ini + .4, fin))
    cuerpo.append(el(logro(250, "Arreglé 1 bug, salieron 3", "Nivel: hidra. Sigue así.", 7), ini + 1.8, fin))
    # escena 3: mi día como dev
    ini, fin = 2 * tramo, T
    barras = [("Escribir código", 15), ("Buscar por qué no funciona", 60), ('"Es un cambio pequeño" (no lo era)', 20), ("Café", 5)]
    for i, (t, v) in enumerate(barras):
        y = 120 + i * 70
        cuerpo.append(el(f'''<text x="80" y="{y}" font-size="19" fill="{TEXTO}">{escape(t)}</text><text x="1120" y="{y}" font-size="19" fill="{AZUL}" text-anchor="end">{v}%</text>
<rect x="80" y="{y+14}" width="1040" height="16" rx="8" fill="{BARRA}" stroke="{BORDE}"/>
<rect x="80" y="{y+14}" width="{1040*v/100:.0f}" height="16" rx="8" fill="{AMBAR if i == 1 else AZUL}"/>''', ini + .3 + i * .45, fin))
    titulos = ["~/mi-proyecto — git log", "~/notificaciones", "~/mi-dia-como-dev — top"]
    for i, t in enumerate(titulos):
        cuerpo.append(el(f'<text x="108" y="40" font-size="18" fill="{TENUE}">{t}</text>', i * tramo, (i + 1) * tramo))
    puntos = "".join(f'<circle cx="{W/2 - 24 + i*24}" cy="{H-28}" r="5" fill="{BORDE}"/>' for i in range(3))
    puntos += "".join(el(f'<circle cx="{W/2 - 24 + i*24}" cy="{H-28}" r="5" fill="{AZUL}"/>', i * tramo, (i + 1) * tramo) for i in range(3))
    marco = f'''<circle cx="34" cy="34" r="7" fill="#ff5f57"/><circle cx="58" cy="34" r="7" fill="#febc2e"/><circle cx="82" cy="34" r="7" fill="#28c840"/>
<text x="{W-32}" y="40" font-size="18" fill="{TENUE}" text-anchor="end">cat memes.txt</text>
<line x1="2" y1="64" x2="{W-2}" y2="64" stroke="{BORDE}" stroke-width="2"/>'''
    guardar("memes.svg", svg(H, marco + "".join(cuerpo) + puntos, "\n".join(css)))


# ---------------------------------------------------------------- 8. logro secreto
def secreto():
    H = 170
    cuerpo = f'''<g class="sube" {d(0.2)}>
<rect x="150" y="30" width="900" height="110" rx="14" fill="{BARRA}" stroke="{AZUL}" stroke-width="1.5"/>
<rect x="176" y="55" width="60" height="60" rx="12" fill="#10213a" stroke="{AZUL}" stroke-width="1.5"/>
<path d="M195 71h22v10a11 11 0 0 1-22 0zM195 75h-6a5 5 0 0 0 6 8M217 75h6a5 5 0 0 1-6 8M206 92v7M198 102h16" fill="none" stroke="{AMBAR}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<text x="262" y="70" font-size="15" fill="{AZUL}" letter-spacing="3">★ LOGRO SECRETO · ACH 10/10</text>
<text x="262" y="102" font-size="24" fill="{TEXTO}" font-weight="bold">Leíste hasta el final</text>
<text x="262" y="126" font-size="16" fill="{SUAVE}">Te debo un café. Escríbeme: portafoliogama.vercel.app</text></g>'''
    guardar("secreto.svg", svg(H, cuerpo))


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    banner()
    for p in DESTACADOS:
        destacado(p)
    construccion()
    otros()
    neofetch()
    arquitectura()
    memes()
    secreto()
