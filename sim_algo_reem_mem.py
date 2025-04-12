#!/usr/bin/env python

# Definiciones iniciales (datos del profe)
marcos_libres = [0x0, 0x1, 0x2]
reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]
segmentos = [
    ('.text', 0x00, 0x1A),
    ('.data', 0x40, 0x28),
    ('.heap', 0x80, 0x1F),
    ('.stack', 0xC0, 0x22),
]

# Función principal
def procesar(segmentos, reqs, marcos_libres):
    tabla_paginas = {}     # página -> marco
    fifo_paginas = []      # orden FIFO
    resultados = []

    for req in reqs:
        # Buscar segmento válido
        segmento = None
        for nombre, base, limite in segmentos:
            if base <= req <= base + limite:
                segmento = (nombre, base)
                break

        if segmento is None:
            resultados.append((req, 0x1FF, "Segmention Fault"))
            continue

        base = segmento[1]
        pagina = req // 16
        offset = req % 16

        if pagina in tabla_paginas:
            marco = tabla_paginas[pagina]
            direccion_fisica = marco * 16 + offset
            resultados.append((req, direccion_fisica, "Marco ya estaba asignado"))
        else:
            if marcos_libres:
                marco = marcos_libres.pop(0)
                tabla_paginas[pagina] = marco
                fifo_paginas.append(pagina)
                direccion_fisica = marco * 16 + offset
                resultados.append((req, direccion_fisica, "Marco libre asignado"))
            else:
                # Reemplazo FIFO
                pagina_remover = fifo_paginas.pop(0)
                marco = tabla_paginas[pagina_remover]
                del tabla_paginas[pagina_remover]
                tabla_paginas[pagina] = marco
                fifo_paginas.append(pagina)
                direccion_fisica = marco * 16 + offset
                resultados.append((req, direccion_fisica, "Marco asignado"))

    return resultados

# Función para imprimir resultados
def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#04x} Direccion Fisica: {result[1]:#04x} Acción: {result[2]}")

# Punto de entrada del script
if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)
