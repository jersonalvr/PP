# paginas/inicio.py
import streamlit as st

def display():
    # Mostrar imagen en la página
    st.image('resources/machine.jpg', use_column_width=True)
    
    # Espaciado
    st.markdown("<br><br>", unsafe_allow_html=True)  # Para dar aire antes del título
    
    # Título centrado
    st.markdown("<h1 style='text-align: center;'>Desarrollo de Modelos Predictivos y Estrategias de Implementación para Optimizar la Productividad y Rentabilidad de los Pescadores Artesanales en la caleta COISHCO - 2024</h1>", unsafe_allow_html=True)
    
    # Espaciado adicional
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Texto introductorio
    st.markdown("""
        <div style='text-align: justify;'>
            <h4 style='text-align: center;'>Introducción</h4>
            La pesca de peces juveniles es una práctica desalentada por el Ministerio de la Producción según la Resolución 
            Ministerial Nº 209-2001-PE, la cual regula las “Tallas Mínimas de Captura y Tolerancia Máxima de Ejemplares 
            Juveniles de los Peces e Invertebrados Marinos”. Esta normativa establece que la extracción de especies de flora 
            o fauna acuática en épocas, cantidades, talla y zonas prohibidas, así como la captura sin el respectivo permiso 
            o excediendo el límite de captura por embarcación, será sancionada con penas privativas de libertad de tres a 
            cinco años. La pesca de productos que no han alcanzado la edad adulta pone en riesgo la reproducción y 
            sostenibilidad de las especies. Para evitar esto, la normativa peruana define tamaños mínimos para la 
            captura de peces y un porcentaje máximo de juveniles que pueden ser pescados accidentalmente, 
            criterios que varían según la especie y se actualizan periódicamente. Sin embargo, algunas embarcaciones 
            descartan en altamar los especímenes de menor tamaño para evitar sanciones, lo que incrementa la mortalidad 
            de los peces y distorsiona la información y monitoreo de las especies, según el IMARPE.<br><br><br>
        </div>
    """, unsafe_allow_html=True)

    # Espaciado adicional después de IMARPE
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Objetivos
    st.markdown("<h3 style='text-align: center;'>Objetivos</h3><br>", unsafe_allow_html=True)        
    st.markdown("""
        Como objetivo general planteamos el siguiente:
        **Determinar las condiciones óptimas para la pesca y su impacto en el valor comercial de diferentes especies, considerando la mejor hora para pescar y la relación entre la talla y el precio.**

        1. Identificar las horas del día más productivas para la pesca artesanal en la caleta Coishco mediante el análisis de la relación entre la hora de captura y el volumen de pesca utilizando modelos predictivos.

        2. Evaluar la relación entre la talla de los peces y su precio por kilogramo, diferenciando entre las distintas especies capturadas en la caleta Coishco, a través de técnicas de regresión aplicadas en Machine Learning.

        3. Comparar los volúmenes de captura obtenidos en diferentes horarios del día para determinar las condiciones más favorables para la pesca artesanal, utilizando análisis predictivos.

        4. Validar un modelo de Machine Learning que permita predecir el volumen de captura y optimizar la estrategia pesquera en función de las condiciones ambientales y biológicas presentes en la caleta Coishco.
    """)
