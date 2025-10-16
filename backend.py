# backend_ga.py
# Algoritmo genético sencillo que acepta parámetros desde el frontend
import random
import math
import copy

AREA_MAXIMA = 50.0  # m²
LADO_PLANO = math.sqrt(AREA_MAXIMA)

# Catálogo por defecto (puedes pasar otro desde el frontend)
CATALOGO_POR_DEFECTO = [
    {"id": 1, "nombre": "Mini nevera", "ancho": 0.5, "largo": 0.5, "ganancia": 40, "stock": 20},
    {"id": 2, "nombre": 'Televisor 32"', "ancho": 0.35, "largo": 0.32, "ganancia": 60, "stock": 6},
    {"id": 3, "nombre": "Lavadora", "ancho": 0.6, "largo": 0.6, "ganancia": 90, "stock": 3},
    {"id": 4, "nombre": "Microondas", "ancho": 0.45, "largo": 0.35, "ganancia": 25, "stock": 8},
    {"id": 5, "nombre": "Aire acondicionado", "ancho": 0.6, "largo": 0.45, "ganancia": 110, "stock": 2},
    {"id": 6, "nombre": "Licuadora", "ancho": 0.2, "largo": 0.2, "ganancia": 8, "stock": 10},
    {"id": 7, "nombre": "Nevera grande", "ancho": 0.8, "largo": 0.75, "ganancia": 220, "stock": 2},
    {"id": 8, "nombre": "Horno eléctrico", "ancho": 0.6, "largo": 0.6, "ganancia": 65, "stock": 3},
    {"id": 9, "nombre": "Aspiradora", "ancho": 0.35, "largo": 0.25, "ganancia": 28, "stock": 6},
    {"id": 10, "nombre": "Plancha", "ancho": 0.25, "largo": 0.15, "ganancia": 10, "stock": 12},
    {"id": 11, "nombre": "Cocina a gas", "ancho": 0.9, "largo": 0.55, "ganancia": 130, "stock": 2},
    {"id": 12, "nombre": "Extractor cocina", "ancho": 0.5, "largo": 0.35, "ganancia": 45, "stock": 4},
]

# ----------------------------
# helpers
# ----------------------------
def area_item(item):
    return item.get('ancho', 0.0) * item.get('largo', 0.0)

def evaluar_individuo(ind, catalogo):
    """Individuo: lista de cantidades (0..stock) por artículo. """
    area = sum(q * area_item(a) for q, a in zip(ind, catalogo))
    ganancia = sum(q * a['ganancia'] for q, a in zip(ind, catalogo))
    if area > AREA_MAXIMA:
        # fuerte penalización
        exceso = area - AREA_MAXIMA
        return ganancia - 1000.0 * exceso
    return ganancia

def crear_individuo_aleatorio(catalogo):
    return [random.randint(0, a.get('stock', 1)) for a in catalogo]

# selección
def seleccion_ruleta(poblacion, fitnesses):
    total = sum(fitnesses)
    if total <= 0:
        return copy.deepcopy(random.choice(poblacion))
    pick = random.uniform(0, total)
    cur = 0.0
    for p, f in zip(poblacion, fitnesses):
        cur += f
        if cur >= pick:
            return copy.deepcopy(p)
    return copy.deepcopy(poblacion[-1])

def seleccion_torneo(poblacion, fitnesses, k=3):
    idxs = random.sample(range(len(poblacion)), min(k, len(poblacion)))
    mejor = max(idxs, key=lambda i: fitnesses[i])
    return copy.deepcopy(poblacion[mejor])

def cruce_un_punto(a, b, pc):
    if random.random() > pc:
        return copy.deepcopy(a), copy.deepcopy(b)
    punto = random.randint(1, len(a)-1)
    hijo1 = a[:punto] + b[punto:]
    hijo2 = b[:punto] + a[punto:]
    return hijo1, hijo2

def mutacion(ind, catalogo, pm):
    for i in range(len(ind)):
        if random.random() < pm:
            # mutar la cantidad: nueva cantidad aleatoria en rango 0..stock
            ind[i] = random.randint(0, catalogo[i].get('stock', 1))
    return ind

# empaquetado simple (shelf / filas) para obtener placements (sin solapamiento)
def empaquetar_con_individuo(ind, catalogo):
    placements = []
    lado_plano = LADO_PLANO
    x = 0.0
    y = 0.0
    fila_alto = 0.0
    margen = 0.02
    # recorrer artículos en orden (puedes ordenar por tamaño si quieres)
    for i, cantidad in enumerate(ind):
        cantidad = int(cantidad)
        if cantidad <= 0:
            continue
        art = catalogo[i]
        w = art.get('ancho', 0.0)
        h = art.get('largo', 0.0)
        for _ in range(cantidad):
            if x + w > lado_plano + 1e-9:
                x = 0.0
                y += fila_alto + margen
                fila_alto = 0.0
            if y + h > lado_plano + 1e-9:
                # no cabe, marcar fuera (no incluido)
                placements.append({'nombre': art['nombre'], 'ancho': w, 'largo': h, 'x': 0.0, 'y': 0.0, 'incluido': False})
                continue
            placements.append({'nombre': art['nombre'], 'ancho': w, 'largo': h, 'x': x, 'y': y, 'incluido': True})
            x += w + margen
            fila_alto = max(fila_alto, h)
    return placements

# ----------------------------
# Ejecutar GA (expuesto)
# ----------------------------
def ejecutar_algoritmo_genetico(params):
    """
    params dict:
      - catalogo: list of items (each: nombre, ancho, largo, ganancia, stock)
      - tam_poblacion
      - generaciones
      - pc
      - pm
      - seleccion: 'torneo' or 'ruleta'
      - elitismo: bool
      - torneo_k (int)
    """
    catalogo = params.get('catalogo', CATALOGO_POR_DEFECTO)
    N = int(params.get('tam_poblacion', 60))
    gen_max = int(params.get('generaciones', 40))
    pc = float(params.get('pc', 0.8))
    pm = float(params.get('pm', 0.1))
    seleccion = params.get('seleccion', 'torneo').lower()
    elitismo = bool(params.get('elitismo', True))
    torneo_k = int(params.get('torneo_k', 3))

    # inicializar poblacion
    poblacion = [crear_individuo_aleatorio(catalogo) for _ in range(N)]
    fitnesses = [evaluar_individuo(ind, catalogo) for ind in poblacion]

    mejor_ind = None
    mejor_fit = -1e18
    historial = []

    for g in range(gen_max):
        # evaluar
        fitnesses = [evaluar_individuo(ind, catalogo) for ind in poblacion]
        # ordenar
        pares = sorted(zip(poblacion, fitnesses), key=lambda x: x[1], reverse=True)
        if pares and pares[0][1] > mejor_fit:
            mejor_fit = pares[0][1]
            mejor_ind = copy.deepcopy(pares[0][0])
        historial.append(pares[0][1] if pares else 0.0)

        nueva = []
        # elitismo
        if elitismo and pares:
            nueva.append(copy.deepcopy(pares[0][0]))

        # reproducir
        while len(nueva) < N:
            if seleccion.startswith('r'):
                p1 = seleccion_ruleta(poblacion, fitnesses)
                p2 = seleccion_ruleta(poblacion, fitnesses)
            else:
                p1 = seleccion_torneo(poblacion, fitnesses, k=torneo_k)
                p2 = seleccion_torneo(poblacion, fitnesses, k=torneo_k)
            c1, c2 = cruce_un_punto(p1, p2, pc)
            c1 = mutacion(c1, catalogo, pm)
            c2 = mutacion(c2, catalogo, pm)
            # reparar si sobrepasa (heurística simple: decrementar elementos con baja eficacia)
            # aquí usamos evaluar_individuo con penalización alta en vez de reparación complicada
            nueva.extend([c1, c2])

        poblacion = nueva[:N]

    # resultado final
    if mejor_ind is None:
        mejor_ind = poblacion[0]
    area_total = sum(q * area_item(a) for q, a in zip(mejor_ind, catalogo))
    gan_total = sum(q * a['ganancia'] for q, a in zip(mejor_ind, catalogo))
    detalle = []
    for q, a in zip(mejor_ind, catalogo):
        detalle.append({
            'nombre': a['nombre'],
            'cantidad': int(q),
            'area_unit': area_item(a),
            'ganancia_unit': a['ganancia'],
            'total': int(q) * a['ganancia']
        })

    placements = empaquetar_con_individuo(mejor_ind, catalogo)

    return {
        'mejor_individuo': mejor_ind,
        'mejor_area': area_total,
        'mejor_ganancia': gan_total,
        'historial': historial,
        'placements': placements,
        'detalle': detalle
    }

# prueba rápida
if __name__ == "__main__":
    res = ejecutar_algoritmo_genetico({'catalogo': CATALOGO_POR_DEFECTO, 'tam_poblacion': 40, 'generaciones': 30})
    print(res.keys())
