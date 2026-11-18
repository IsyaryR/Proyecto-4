import os
import math
import random
import shutil
import subprocess

from GrafoLib import (
    grafoMalla, grafoErdosRenyi, grafoGilbert,
    grafoGeografico, grafoBarabasiAlbert, grafoDorogovtsevMendes
)

# ---------------------------------------------------------
#  Configuracion
# ---------------------------------------------------------
TAMANOS = [30,150]          # numero de nodos de cada grafo
PESO_MIN, PESO_MAX = 1, 10   # rango de pesos aleatorios de las aristas
SEMILLA = 42                 # None para resultados distintos en cada ejecucion
GENERAR_PNG = True           # si Graphviz esta instalado, tambien crea imagenes .png

CARPETA_GEN = os.path.join("resultados", "generados")       # grafos originales
CARPETA_KD  = os.path.join("resultados", "kruskal_directo") # arboles Kruskal directo
CARPETA_KI  = os.path.join("resultados", "kruskal_inverso") # arboles Kruskal inverso
CARPETA_P   = os.path.join("resultados", "prim")            # arboles Prim
for c in (CARPETA_GEN, CARPETA_KD, CARPETA_KI, CARPETA_P):
    os.makedirs(c, exist_ok=True)

if SEMILLA is not None:
    random.seed(SEMILLA)


def dimensionesMalla(n):
    # Busca filas x columnas con exactamente n nodos, lo mas cuadrada posible
    for filas in range(int(math.sqrt(n)), 0, -1):
        if n % filas == 0:
            return filas, n // filas


def renderizar(ruta_dot, motor="dot"):
    # Convierte el .dot a .png con Graphviz (si esta instalado)
    if not GENERAR_PNG or shutil.which(motor) is None:
        return
    subprocess.run([motor, "-Tpng", ruta_dot, "-o", ruta_dot.replace(".dot", ".png")], check=True)


def guardar(g, carpeta, archivo, titulo=None, motor="dot"):
    ruta = os.path.join(carpeta, archivo + ".dot")
    g.guardarGraphViz(ruta, archivo, titulo=titulo)
    renderizar(ruta, motor)


def procesar(nombre, g, n):
    base = f"{nombre}_{n}"

    # 1) Pesos aleatorios y .dot del grafo generado
    g.asignarPesosAleatorios(PESO_MIN, PESO_MAX)
    guardar(g, CARPETA_GEN, base, motor="neato" if n > 30 else "dot")

    # 2) Arboles de expansion minima con los tres algoritmos
    resultados = {
        "KruskalD": (g.KruskalD(), CARPETA_KD),
        "KruskalI": (g.KruskalI(), CARPETA_KI),
        "Prim":     (g.Prim(),     CARPETA_P),
    }
    costos = []
    for algoritmo, (arbol, carpeta) in resultados.items():
        costo = sum(a.peso for a in arbol.aristas)
        costos.append(costo)
        titulo = f"{algoritmo} - {base}: costo total = {costo:.2f}"
        guardar(arbol, carpeta, f"{base}_{algoritmo}", titulo=titulo)

    # 3) Resumen en consola: los tres costos deben ser iguales
    arbol = resultados["KruskalD"][0]
    componentes = len(g.nodos) - len(arbol.aristas)
    iguales = "OK" if max(costos) - min(costos) < 1e-9 else "DIFERENTES"
    print(f"  {nombre:<18} nodos={len(g.nodos):>4} aristas={len(g.aristas):>5} | "
          f"MST aristas={len(arbol.aristas):>4} | KD={costos[0]:8.2f}  KI={costos[1]:8.2f}  "
          f"Prim={costos[2]:8.2f}  [{iguales}]")
    if componentes > 1:
        print(f"  {'':<18} grafo no conexo: {componentes} componentes -> bosque de expansion minima")


for N in TAMANOS:
    print(f"\n=== N = {N} ===")
    filas, cols = dimensionesMalla(N)
    #procesar(f"Malla_{filas}x{cols}", grafoMalla(filas, cols), N)
    #procesar("ErdosRenyi", grafoErdosRenyi(N, 2 * N), N)
    #procesar("Gilbert", grafoGilbert(N, min(0.15, 4 / N)), N)
    procesar("Geografico", grafoGeografico(N, 0.3 if N <= 30 else 0.2), N)
    #procesar("BarabasiAlbert", grafoBarabasiAlbert(N, 3), N)
    #procesar("DorogovtsevMendes", grafoDorogovtsevMendes(N), N)

print("\nArchivos .dot guardados en la carpeta 'resultados':")
print(f"  {CARPETA_GEN}\n  {CARPETA_KD}\n  {CARPETA_KI}\n  {CARPETA_P}")