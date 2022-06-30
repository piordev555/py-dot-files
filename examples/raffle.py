# -*- coding: utf-8 -*-
import csv

archivo = 'asistentes.csv'
columna_nombre = 2
columna_apellido = 3
columna_email = 4
columna_filtro = 10
asistentes = []

for fila in csv.reader(open(archivo, 'r')):
    if fila[columna_filtro] in ['Sí', 'Si', 'Asistió', 'asistió']:
        asistentes.append((
            fila[columna_nombre],
            fila[columna_apellido],
            fila[columna_email],
        ))

while True:
    input('Presione ENTER para mostrar el próximo ganador...')
    asistentes.shuffle()
    print(asistentes.pop())
