from flask import Flask, render_template, request, jsonify
from scipy.integrate import quad
from flask_cors import CORS

# Crear una instancia de la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para manejar solicitudes desde otros dominios

# Diccionario con los coeficientes de Joback para cada grupo funcional
coeficientes_joback = {
    '-CH3': (19.5, -0.00808, 0.000153, -0.000000097),
    '>CH2': (9.0, 0.103, -0.000210, 0),
    # Otros grupos funcionales...
}

def calcular_cp_integral(grupos_funcionales, temperatura_min, temperatura_max):
    """
    Calcular el calor específico por integración numérica.
    """
    # Importar la función de integración
    from scipy.integrate import quad

    # Inicializar acumuladores para los coeficientes ajustados
    suma_a = suma_b = suma_c = suma_d = 0
    
    # Sumar los coeficientes para cada grupo funcional
    for grupo, cantidad in grupos_funcionales.items():
        if grupo in coeficientes_joback:
            a, b, c, d = coeficientes_joback[grupo]
            suma_a += cantidad * a
            suma_b += cantidad * b
            suma_c += cantidad * c
            suma_d += cantidad * d
        else:
            return None, "Grupo funcional no encontrado"

    # Definir la función a integrar
    def integrand(temperatura):
        return (suma_a - 37.93) + (suma_b + 0.210) * temperatura + (suma_c - 3.91e-4) * temperatura**2 + (suma_d + 2.06e-7) * temperatura**3

    # Realizar la integración numérica
    cp_integral, _ = quad(integrand, temperatura_min, temperatura_max)
    
    # Crear la fórmula para mostrar
    formula = f"CP = ({suma_a} - 37.93) + ({suma_b} + 0.210) * T + ({suma_c} - 3.91e-4) * T^2 + ({suma_d} + 2.06e-7) * T^3"
    
    return cp_integral, formula

@app.route('/calcular', methods=['POST'])
def calcular():
    """
    Manejar la solicitud POST para calcular el calor específico.
    """
    # Extraer datos JSON de la solicitud
    data = request.json
    grupos_funcionales = data.get('grupos_funcionales', {})
    temperatura_min = data.get('temperatura_min', 298.15)
    temperatura_max = data.get('temperatura_max', 298.15)

    # Verificar que la temperatura mínima sea menor que la máxima
    if temperatura_min >= temperatura_max:
        return jsonify({'error': 'La temperatura mínima debe ser menor que la temperatura máxima.'})

    # Calcular el calor específico y obtener la fórmula
    resultado, formula = calcular_cp_integral(grupos_funcionales, temperatura_min, temperatura_max)
    
    # Devolver el resultado y la fórmula en formato JSON
    return jsonify({
        'cp_promedio': resultado,
        'formula': formula
    })

# Ejecutar la aplicación en modo de depuración
if __name__ == '__main__':
    app.run(debug=True)
