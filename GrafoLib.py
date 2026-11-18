import random
import math
import heapq
from collections import deque


class Nodo:
    def __init__(self, id):
        self.id = id #identificador unico


class Arista:
    def __init__(self, u, v, peso=1.0):
        self.u = u  # Nodo origen
        self.v = v  # Nodo destino
        self.peso = peso  # Costo de la arista


class ConjuntosDisjuntos:
    # Estrcutura en Kruskal directo para saber si dos nodos ya estan en el mismo componente; evitar ciclos
    def __init__(self, elementos):
        self.padre = {e: e for e in elementos} #cada nodo empieza siendo su propio representante
        self.rango = {e: 0 for e in elementos} #altura aproximada de cada arbol

    def encontrar(self, x): #regresa el representante del conjunto de x (con compresion de camino)
        while self.padre[x] != x:
            self.padre[x] = self.padre[self.padre[x]]
            x = self.padre[x]
        return x

    def unir(self, a, b): #une los conjuntos de a y b; regresa False si ya estaban unidos
        ra, rb = self.encontrar(a), self.encontrar(b)
        if ra == rb:
            return False
        if self.rango[ra] < self.rango[rb]: #el arbol mas bajo cuelga del mas alto
            ra, rb = rb, ra
        self.padre[rb] = ra
        if self.rango[ra] == self.rango[rb]:
            self.rango[ra] += 1
        return True


class Grafo:
    def __init__(self, dirigido=False):
        self.dirigido = dirigido # si es false A -- B; si es true A -> B no implica B -> A
        self.nodos = {} #diccionario de nodos registrados id -> Nodo
        self.aristas = [] #lista con todas las aristas
        self.adyacencia = {}  # Diccionario para guardar vecinos de cada nodo id -> set(id_vecino)

    def agregarNodo(self, nodo): #Funcion para agregar nodo
        if nodo.id not in self.nodos:
            self.nodos[nodo.id] = nodo
            self.adyacencia[nodo.id] = set()
        return self.nodos[nodo.id]

    def agregarArista(self, u, v, peso=1.0): #Conecta dos nodos con un peso
        if u.id not in self.nodos:
            self.agregarNodo(u)
        if v.id not in self.nodos:
            self.agregarNodo(v)

        # Evitar aristas duplicadas
        if v.id in self.adyacencia[u.id]:
            return None

        arista = Arista(u, v, peso)
        self.aristas.append(arista)
        self.adyacencia[u.id].add(v.id)
        if not self.dirigido:
            self.adyacencia[v.id].add(u.id)
        return arista

    def asignarPesosAleatorios(self, minimo=1.0, maximo=10.0, decimales=2):
        #Asigna a cada arista un peso aleatorio uniforme en [minimo, maximo]
        for a in self.aristas:
            a.peso = round(random.uniform(minimo, maximo), decimales)

    # =====================================================
    #  Arbol de expansion minima (MST)
    #  Los tres metodos regresan un NUEVO Grafo no dirigido
    #  con los mismos nodos y solo las aristas del arbol.
    #  - Si el grafo no es conexo se obtiene un BOSQUE de
    #    expansion minima (un arbol por cada componente).
    #  - Si el grafo es dirigido se ignora la direccion de
    #    las aristas (el MST se define sobre grafos no dirigidos).
    # =====================================================
    def _aristasNoDirigidas(self):
        #Lista de aristas (u_id, v_id, peso) sin direccion ni duplicados.
        #Si existen u->v y v->u se conserva la de menor peso.
        mejores = {}
        for a in self.aristas:
            if a.u.id == a.v.id: #los lazos nunca forman parte de un arbol
                continue
            clave = frozenset((a.u.id, a.v.id))
            if clave not in mejores or a.peso < mejores[clave][2]:
                mejores[clave] = (a.u.id, a.v.id, a.peso)
        return list(mejores.values())

    def _arbolVacio(self): #Grafo no dirigido con los mismos nodos y sin aristas
        arbol = Grafo(dirigido=False)
        for i in self.nodos:
            arbol.agregarNodo(Nodo(i))
        return arbol

    @staticmethod
    def _conectados(ady, origen, destino): #BFS: ¿existe un camino origen -> destino?
        visitados = {origen}
        cola = deque([origen])
        while cola:
            x = cola.popleft()
            if x == destino:
                return True
            for y in ady[x]:
                if y not in visitados:
                    visitados.add(y)
                    cola.append(y)
        return False

    #-----------------------------------------------------
    #  Kruskal directo
    #  1) Ordena las aristas de menor a mayor peso.
    #  2) Recorre la lista y agrega cada arista si NO forma
    #     un ciclo, sus extremos estan en componentes
    #     distintos.
    #-----------------------------------------------------
    def KruskalD(self):
        arbol = self._arbolVacio()
        conjuntos = ConjuntosDisjuntos(self.nodos.keys())
        maximo = len(self.nodos) - 1  #un arbol con n nodos tiene n-1 aristas

        for (u, v, w) in sorted(self._aristasNoDirigidas(), key=lambda t: t[2]):
            if conjuntos.unir(u, v): #u y v estaban separados -> no hay ciclo
                arbol.agregarArista(arbol.nodos[u], arbol.nodos[v], w)
                if len(arbol.aristas) == maximo: #arbol completo, se puede terminar
                    break
        return arbol

    #-----------------------------------------------------
    #  Kruskal inverso 
    #  1) Empieza con todas las aristas del grafo.
    #  2) Las recorre de mayor a menor peso y elimina cada
    #     una, salvo que al quitarla se desconecten sus
    #     extremos, en ese caso la arista se conserva.
    #-----------------------------------------------------
    def KruskalI(self):
        aristas = sorted(self._aristasNoDirigidas(), key=lambda t: t[2], reverse=True)

        ady = {i: {} for i in self.nodos}  #id -> {vecino: peso} del grafo que se va reduciendo
        for (u, v, w) in aristas:
            ady[u][v] = w
            ady[v][u] = w

        for (u, v, w) in aristas:
            del ady[u][v] #se intenta quitar la arista
            del ady[v][u]
            if not self._conectados(ady, u, v): #era un puente: se vuelve a poner
                ady[u][v] = w
                ady[v][u] = w

        arbol = self._arbolVacio()
        for u in ady:
            for v, w in ady[u].items(): #agregarArista ignora la arista repetida v -- u
                arbol.agregarArista(arbol.nodos[u], arbol.nodos[v], w)
        return arbol

    #-----------------------------------------------------
    #  Prim
    #  1) Empieza en un nodo y lo marca como visitado.
    #  2) Con una cola de prioridad elige siempre la arista
    #     mas barata que conecta un nodo visitado con uno
    #     NO visitado y la agrega al arbol.
    #  3) Si quedan nodos sin visitar (grafo no conexo),
    #     reinicia desde uno de ellos.
    #-----------------------------------------------------
    def Prim(self):
        ady = {i: {} for i in self.nodos}  #vecinos con peso, sin direccion
        for (u, v, w) in self._aristasNoDirigidas():
            ady[u][v] = w
            ady[v][u] = w

        arbol = self._arbolVacio()
        visitados = set()
        contador = 0  #desempate en la cola para no comparar ids

        for inicio in self.nodos:
            if inicio in visitados:
                continue
            visitados.add(inicio)
            cola = []
            for v, w in ady[inicio].items():
                heapq.heappush(cola, (w, contador, inicio, v))
                contador += 1

            while cola:
                w, _, u, v = heapq.heappop(cola) #arista mas barata de la frontera
                if v in visitados: #ambos extremos ya estan en el arbol -> formaria ciclo
                    continue
                visitados.add(v)
                arbol.agregarArista(arbol.nodos[u], arbol.nodos[v], w)
                for x, wx in ady[v].items(): #nuevas aristas de la frontera
                    if x not in visitados:
                        heapq.heappush(cola, (wx, contador, v, x))
                        contador += 1
        return arbol

    def _paresPosibles(self): #Devuelve todos los pares (i, j) con i < j sobre los ids actuales.
        ids = list(self.nodos.keys()) #diccionario donde las claves son los nodos [0,1,2,3]
        pares = [] #lista vacia para guardar cada pareja en forma de tupla
        for i in range(len(ids)):
            for j in range(i+1, len(ids)):
                pares.append((ids[i], ids[j]))
        return pares #[(0,1),(0,2),(1,2),...]

    def guardarGraphViz(self, ruta, nombre="Grafo", titulo=None, mostrarPesos=True):
        #Guarda el grafo en formato DOT (GraphViz). Nodos como "nodo_i" y pesos en las aristas.
        tipo = "digraph" if self.dirigido else "graph"
        conector = "->" if self.dirigido else "--"

        lineas = [f'{tipo} {nombre} {{']
        if titulo: #texto que aparece debajo del dibujo (ej. costo total del arbol)
            lineas.append(f'    label="{titulo}";')
            lineas.append('    labelloc="b";')
        for i in self.nodos:
            lineas.append(f'    "nodo_{i}";')
        for a in self.aristas:
            extra = f' [label="{a.peso:g}"]' if mostrarPesos else ""
            lineas.append(f'    "nodo_{a.u.id}" {conector} "nodo_{a.v.id}"{extra};')
        lineas.append("}")

        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))
# =========================================================
#  Funciones de generacion de grafos
# =========================================================
#---------------------------------------
#         Grafo de malla m x n.
#  Conecta cada nodo con su vecino de
#  la derecha y su vecino de abajo
#---------------------------------------
def grafoMalla(m, n, dirigido=False):
    if m<1 or n<1:#Validacion de la malla minimo 1 fila y minimo 1 columna
        raise ValueError("m y n deben ser >= 1")
    g=Grafo(dirigido=dirigido)#instancia vacia

    for i in range(m): #recorre las filas de 0 a m-1
        for j in range(n):#recorre las columnas de 0 a n-1
            g.agregarNodo(Nodo(i*n+j))

    for i in range(m):
        for j in range(n):
            actual=g.nodos[i*n+j]
            if i+1 < m: #conexion vertical con el nodo de abajo
                g.agregarArista(actual, g.nodos[(i+1)*n+j])
            if j+1 < n: #conexion horizontal con el nodo de la derecha
                g.agregarArista(actual, g.nodos[i*n+(j+1)])
    return g
#---------------------------------------------------------
#  Grafo aleatorio Erdos-Renyi con n nodos y m aristas.
# Obtiene las posibles parejas de nodos posibles para conectarse
#---------------------------------------------------------
def grafoErdosRenyi(n, m, dirigido=False):
    if n <= 0: #verifica que numero de nodos n sea mayor a 0
        raise ValueError("n debe ser > 0")
    g = Grafo(dirigido=dirigido)#grafo vacio
    for i in range(n): #crea n nodos ennumerados de 0 a n-1
        g.agregarNodo(Nodo(i))

    max_aristas = n*(n-1) if dirigido else n*(n-1) // 2 #calculo de aristas unicas maximas en el grafo
    if m > max_aristas:
        raise ValueError(f"m={m} excede el máximo posible de aristas ({max_aristas})")

    pares = g._paresPosibles()#regresa lista con todos los pares (u,v)  u<v
    if dirigido: #si es dirigido, duplica pares por el sentido inverso de cada combinacion
        pares_dir = []
        for (u, v) in pares:
            pares_dir.append((u, v))
            pares_dir.append((v, u))
        pares = pares_dir

    for (u_id, v_id) in random.sample(pares, m):#Elige m elementos de la lista pares sin repeticion y uniforme
        g.agregarArista(g.nodos[u_id], g.nodos[v_id])
    return g
#-----------------------------------------------------------
#  Grafo aleatorio Gilbert con cada arista con probabilidad p.
#  Grafo aleatorio basado en probabilidad
#-----------------------------------------------------------
def grafoGilbert(n, p, dirigido=False):
    if n <= 0: #validacion de numeros positivos
        raise ValueError("n debe ser > 0")
    if not (0.0 <= p <= 1.0):#probabilidad entre 0 a 100%
        raise ValueError("p debe estar en [0, 1]")
    g = Grafo(dirigido=dirigido)
    for i in range(n): #crea n nodos iniciales del 0 al n-1
        g.agregarNodo(Nodo(i))

    for (u_id, v_id) in g._paresPosibles():#recorre todas las combinaciones posibles de pares de nodos
        if random.random() < p: #compara el numero decimal general aleatorio con la probabilidad de p
            g.agregarArista(g.nodos[u_id], g.nodos[v_id])
        if dirigido and random.random() < p: #segundo lanzamiento para ver si existe arista en sentido contrario
            g.agregarArista(g.nodos[v_id], g.nodos[u_id])
    return g
#--------------------------------------------------------------------
#   Grafo geografico: nodos en [0,1]^2, arista si distancia <= r.
# Simula nodos ubicados en un cuadrado de 1 x 1 (Plano 2D)
#--------------------------------------------------------------------
def grafoGeografico(n, r, dirigido=False):
    if n <= 0: #validacion de nodos mayor a 0
        raise ValueError("n debe ser > 0")
    if not (0.0 < r < 1.0):#radio de cobertura dentro de 0 a 1
        raise ValueError("r debe estar en (0, 1)")
    g = Grafo(dirigido=dirigido)
    coords = [] #lista de coordenadas para guardar la posicion de cada nodo
    for i in range(n): #posicionamiento de nodos
        coords.append((random.random(), random.random()))#para cada nodo asigna una coordenada aleatoria
        g.agregarNodo(Nodo(i)) #añade tupla a lista de coords y registra nodo(i) en grafo

    for i in range(n):
        for j in range(i+1, n):
            xi, yi = coords[i] #extrae coordenadas de nodo i
            xj, yj = coords[j] #extrae coordenadas de nodo j
            if math.hypot(xi-xj, yi-yj) <= r: #teorema de pitagoras para distancia euclidiana, si  la distancia es <= r crea la arista
                g.agregarArista(g.nodos[i], g.nodos[j])
                if dirigido:# si es dirigido añade la arista en sentido inverso
                    g.agregarArista(g.nodos[j], g.nodos[i])
    return g
#---------------------------------------------------------
#           Grafo aleatorio Barabasi-Albert.
#---------------------------------------------------------
def grafoBarabasiAlbert(n, d, dirigido=False):
    if n <= 0:#Validacion
        raise ValueError("n debe ser > 0")
    if d < 1:
        raise ValueError("d debe ser >= 1")
    if d >= n:# inicializacion
        d = n - 1

    g = Grafo(dirigido=dirigido)
    for i in range(n):
        g.agregarNodo(Nodo(i))

    iniciales = min(d+1, n)# crea iniciales con d+1
    for i in range(iniciales):
        for j in range(i+1, iniciales):
            g.agregarArista(g.nodos[i], g.nodos[j])

    for nuevo in range(iniciales, n):#para cada nodo que ingresa
        existentes = list(range(nuevo))#lista de id de nodos que forman parte dle grafo
        grados = [max(len(g.adyacencia[k]), 1) for k in existentes]#cuantas conexiones tiene cada nodo

        seleccionados = set() #se usa set() y while para garantizar que el nuevo nodo eliga d vecinos diferentes sin duplicar conexiones
        while len(seleccionados) < d and len(seleccionados) < len(existentes):
            elegido = random.choices(existentes, weights=grados, k=1)[0]
            seleccionados.add(elegido)

        for objetivo in seleccionados:#crea d aristas entre el nodo nuevo y cada nodo objetivo elegido
            g.agregarArista(g.nodos[nuevo], g.nodos[objetivo])
            if dirigido:
                g.agregarArista(g.nodos[objetivo], g.nodos[nuevo])
    return g
#---------------------------------------------------------
#        Grafo aleatorio Dorogovtsev-Mendes.
#---------------------------------------------------------
def grafoDorogovtsevMendes(n, dirigido=False):
    if n<3:# requiere 3 nodos minimo para el triangulo
        raise ValueError("n debe ser >= 3")
    g = Grafo(dirigido=dirigido)
    for i in range(3): #crea la estructura del grafo con 3 nodos(0,1,2)
        g.agregarNodo(Nodo(i))
    #conecta los nodos 0,1 y 2 para formar triangulo
    g.agregarArista(g.nodos[0], g.nodos[1])
    g.agregarArista(g.nodos[1], g.nodos[2])
    g.agregarArista(g.nodos[2], g.nodos[0])
    #Para cada nuevo nodo desde 3 a n-1
    for nuevo in range(3, n):
        g.agregarNodo(Nodo(nuevo))#registra nodo nuevo
        arista = random.choice(g.aristas)#elige una arista al azar
        u, v = arista.u, arista.v #extrae extremos de u y v
        #conecta nodo nuevo con u y v para formar nuevo triangulo
        g.agregarArista(g.nodos[nuevo], u)
        g.agregarArista(g.nodos[nuevo], v)
        if dirigido:
            g.agregarArista(u, g.nodos[nuevo])
            g.agregarArista(v, g.nodos[nuevo])
    return g