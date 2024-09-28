import re
from collections import defaultdict
from flask import Flask, Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import mongo, init_db
from bson.objectid import ObjectId
from sympy.logic.boolalg import And, Or, Not

compuertas_bp = Blueprint('compuertas_bp', __name__)

# Definimos los patrones para las operaciones lógicas
patrones = {
    'NOT': r'!\w+',       # Busca expresiones como !b
    'AND': r'\w+\s*\*\s*\w+',  # Busca expresiones como a*b
    'OR': r'\w+\s*\+\s*\w+',   # Busca expresiones como a+b
}

# Función para normalizar las operaciones (para que a + c sea igual que c + a)
def normalizar_operacion(operacion):
    operacion = operacion.replace(' ', '')  # Elimina los espacios
    # Si es una operación AND u OR, ordenar los operandos alfabéticamente
    if '*' in operacion or '+' in operacion:
        operandos = re.split(r'[\*\+]', operacion)
        operandos = sorted(operandos, key=lambda x: x.strip())  # Ordenar operandos
        operacion = ' * '.join(operandos) if '*' in operacion else ' + '.join(operandos)
    return operacion.strip()

# Función para contar operaciones e identificar cuáles se repiten
def analizar_expresiones(expresiones):
    # Diccionario para almacenar las operaciones en cada expresión
    operaciones_por_expresion = defaultdict(list)
    
    # Diccionario para almacenar cuántas veces se repite cada operación en total
    conteo_operaciones = defaultdict(int)

    for expr in expresiones:
        print(f"\nAnalizando: {expr}")
        for operacion, patron in patrones.items():
            # Encuentra todas las coincidencias en la expresión
            coincidencias = re.findall(patron, expr)
            if coincidencias:
                # Normalizar las operaciones encontradas
                coincidencias = [normalizar_operacion(op) for op in coincidencias]
                # Añade las operaciones encontradas al diccionario
                operaciones_por_expresion[expr].extend(coincidencias)
                # Cuenta cuántas veces aparece cada operación
                for op in coincidencias:
                    conteo_operaciones[normalizar_operacion(op)] += 1
        
        # Imprime las operaciones encontradas para la expresión actual
        print(f"Operaciones encontradas: {operaciones_por_expresion[expr]}")

    return operaciones_por_expresion, conteo_operaciones

# Función para comparar las operaciones entre expresiones
def comparar_expresiones(operaciones_por_expresion):
    comparaciones = defaultdict(list)
    
    expresiones = list(operaciones_por_expresion.keys())
    for i in range(len(expresiones)):
        expr1 = expresiones[i]
        for j in range(i+1, len(expresiones)):
            expr2 = expresiones[j]
            # Comparamos las operaciones de expr1 y expr2
            operaciones_comunes = set(map(normalizar_operacion, operaciones_por_expresion[expr1])) & set(map(normalizar_operacion, operaciones_por_expresion[expr2]))
            if operaciones_comunes:
                comparaciones[f"{expr1} <-> {expr2}"] = list(operaciones_comunes)
    
    return comparaciones

# Ejemplo de expresiones
expresiones = [
    '(a * c) + (!(a + c)) + b',
    '(!a) + (!(b+c)) + (b*c)',
    'a + c + (!b)',
    '(b * (!a))+ (a*(!b)*c) + ((!a)*(!c)) + (b*(!c))',
    '(!c)*(b+(!a))',
    '(a*(!b))+ (a*(!c))+ ((!b)*(!c))',
    '(b*(!c))'
]

# Paso 1: Analizar las expresiones para encontrar y contar operaciones
operaciones_por_expresion, conteo_operaciones = analizar_expresiones(expresiones)

# Paso 2: Comparar las expresiones entre sí para encontrar operaciones comunes
comparaciones = comparar_expresiones(operaciones_por_expresion)

# Imprimir los resultados
print("\nOperaciones en cada expresión:")
for expr, ops in operaciones_por_expresion.items():
    print(f"{expr}: {ops}")

print("\nOperaciones repetidas entre expresiones:")
for comparacion, ops_comunes in comparaciones.items():
    print(f"{comparacion}: {ops_comunes}")

print("\nConteo total de operaciones:")
for operacion, conteo in conteo_operaciones.items():
    print(f"{operacion}: {conteo}")
