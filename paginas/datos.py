import streamlit as st
import pandas as pd 

def display():
    # Título del Proyecto
    st.markdown("<h1 style='text-align: center;'>Supervisión y Análisis de Datos de Pesca Artesanal en la Región de Áncash</h1>", unsafe_allow_html=True)

    # Cargar los datos
    df = pd.read_excel('data/data.xlsx')
    st.write("### Vista previa de los datos")
    st.write(df.head(30))

    # Descripción General del Proyecto
    st.write("### Descripción del Proyecto")
    st.markdown("""
    Este proyecto tiene como objetivo la recopilación, supervisión y análisis de datos sobre el volumen de descarga, especie, y precios de los recursos hidrobiológicos en los diferentes puntos de desembarque artesanal en la región de Áncash. La información obtenida permite cuantificar la productividad real de la pesca artesanal y generar información confiable para la toma de decisiones y la mejora de las políticas públicas en el sector.
    """)

    # Finalidad del Proyecto
    st.write("### Finalidad Pública del Proyecto")
    st.markdown("""
    En el marco del Programa Presupuestal 095: **Fortalecimiento de la Pesca Artesanal**, este proyecto busca fortalecer el **Sistema de Información de Desembarque Artesanal**. La recopilación de datos precisos y detallados permite realizar análisis sobre la comercialización de recursos pesqueros y ofrecer mejores oportunidades tanto para los pescadores como para el sector en general.
    """)

    # Objetivo Específico
    st.write("### Objetivo Específico")
    st.markdown("""
    El objetivo principal de este proyecto es la recopilación de datos sobre los precios y volúmenes de los recursos hidrobiológicos, como los desembarcados en los puertos de **Coishco, Áncash**, durante todo el año. Estos datos se recogen mensualmente y se usan para realizar informes sobre la situación de la pesca artesanal en la región.
    """)

    # Datos Recopilados
    st.write("### Variables Recopiladas")
    st.markdown("""
    Los datos recopilados incluyen:
    - Nombre común de la especie
    - Nombre científico de la especie
    - Cantidad (kg)
    - Aparejo utilizado
    - Procedencia de la pesca
    - Nombre de la embarcación y su matrícula
    - Número de tripulantes
    - Número de días y horas de faena
    - Hora de descarga
    - Tamaño de las especies
    - Precios de playa (por kg)
    - Destino de los recursos (venta)
    """)

    # Fuentes de Datos
    st.write("### Fuentes de Datos Utilizadas")
    st.markdown("""
    La información obtenida en este proyecto proviene de diversas fuentes, tanto locales como internacionales:

    1. **Encuestas en campo**: Datos recopilados directamente de pescadores, patrones y administradores en los puntos de desembarque artesanal.
    2. **Ministerio de la Producción (PRODUCE)**: Validación y supervisión de los datos recolectados, en el marco del **Decreto Supremo N° 002-2017-PRODUCE** y el **Programa Presupuestal 095**.
    3. **[NOAA](https://www.noaa.gov)** (National Oceanic and Atmospheric Administration): Proporciona datos históricos y actuales de temperatura y salinidad del agua para las zonas costeras.
    4. **[Copernicus](https://marine.copernicus.eu)**: Plataforma europea de monitoreo ambiental que ofrece datos sobre corrientes marinas, temperaturas y salinidad.
    5. **[Windy](https://www.windy.com)**: Información en tiempo real sobre la velocidad del viento, que se ajusta en función de la hora de inicio de faena.
    6. **Datos geográficos locales**: Información sobre la profundidad de las zonas pesqueras de la región de Áncash, obtenida de estudios regionales y geográficos, como el **[Atlas Geográfico del Perú](http://www.ign.gob.pe/atlas)** y el **[Instituto del Mar del Perú (IMARPE)](http://www.imarpe.pe)**.
    7. **[OSINERGMIN](https://www.osinergmin.gob.pe/seccion/institucional/Paginas/VisorPreciosReferencia.aspx)**: Fuente para los precios de referencia de los combustibles utilizados en las embarcaciones pesqueras.
    8. **[PRODUCE](https://consultasenlinea.produce.gob.pe/ConsultasEnLinea/consultas.web/embarcacion#)**: Información sobre los modelos de motor de las embarcaciones pesqueras, disponible a través de la plataforma de consultas del Ministerio de la Producción.
    """)

    # Descripción de los Cálculos
    st.write("### Descripción de los Cálculos")

    st.markdown("""
    **1. Cálculo de las Millas Recorridas:**

    Se utiliza la siguiente fórmula basada en la ley del coseno esférico para determinar la distancia entre el origen (lugar de pesca) y el destino (muelle):
    """)
    st.latex(r"""
    \text{Millas\_Recorridas} = 2 \times 3958.8 \times \arcsin\left(\sqrt{\left(\sin\left(\frac{\text{radians}(\Delta \text{Lat})}{2}\right)\right)^2 + \cos(\text{radians}(\text{OR\_Lat})) \times \cos(\text{radians}(\text{Dest\_Lat})) \times \left(\sin\left(\frac{\text{radians}(\Delta \text{Lon})}{2}\right)\right)^2}\right)
    """)
    st.markdown("""
    Donde:
    """)
    st.latex(r"""
    \Delta \text{Lat} = \text{Latitud de Destino} - \text{Latitud de Origen}
    """)
    st.latex(r"""
    \Delta \text{Lon} = \text{Longitud de Destino} - \text{Longitud de Origen}
    """)

    # Fórmula para el cálculo de los costos de combustible
    st.markdown("""
    **2. Cálculo de los Costos de Combustible:**

    El costo de combustible se calcula en función de las millas recorridas, el volumen de pesca, y el precio del galón de combustible. La fórmula es:
    """)
    st.latex(r"""
    \text{Costo\_Combustible} = \left(\text{Millas\_Recorridas} \times 0.05 \div 2 \times \left(1 + 1 + \text{Volumen} \times 0.0001\right)\right) \times \text{Precio\_Galón}
    """)

    # Fórmula para el cálculo de la ganancia
    st.markdown("""
    **3. Cálculo de la Ganancia:**

    Finalmente, la ganancia se obtiene restando los costos de combustible del valor total de las ventas:
    """)
    st.latex(r"""
    \text{Ganancia} = \text{Venta} - \text{Costo\_Combustible}
    """)

    # Fórmula para el cálculo del CPUE
    st.markdown("""
    **4. Cálculo del CPUE (Índice de Captura por Unidad de Esfuerzo):**

    El **CPUE** se calcula dividiendo el volumen capturado (en kilogramos) por el esfuerzo de pesca, el cual es medido por las millas recorridas multiplicado por el tiempo de faena (en horas):
    """)
    st.latex(r"""
    \text{CPUE} = \frac{\text{Volumen\_Kg}}{\text{Millas\_Recorridas} \times \text{Tiempo\_Faena}}
    """)

    # Información Adicional
    st.write("### Información Adicional")
    st.markdown("""
    Este proyecto se realiza de manera continua a lo largo del año, con reportes mensuales y análisis detallados para cada temporada. Los datos recopilados son clave para mejorar la toma de decisiones en el sector pesquero, promoviendo tanto el desarrollo económico como la sostenibilidad de la pesca artesanal en la región.
    """)

