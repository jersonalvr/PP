# paginas/eda.py
import streamlit as st
import pandas as pd  
import plotly.express as px
import seaborn as sns
import folium
import numpy as np
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from streamlit_folium import folium_static

def display():
    # Configuración de la página
    st.markdown("<h2 style='text-align: center;'>Página de análisis exploratorio de datos (EDA)</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if 'subpagina_eda' not in st.session_state:
        st.markdown("<h4 style='text-align: center;'>En esta sección de nuestro proyecto, te ofrecemos la oportunidad de explorar un análisis detallado de los datos a través de diversos gráficos y visualizaciones. Este espacio está diseñado para que puedas entender mejor y analizar de forma intuitiva la información que hemos recopilado.</h4>", unsafe_allow_html=True)
        # Crear tres columnas, la del medio contendrá la imagen
        col1, col2, col3 = st.columns([1,2,1])
        
        # Mostrar la imagen en la columna del medio
        with col2:
            st.image('resources/EDA.jpg')

    # Cargar los datos
    @st.cache_data  # Cachear los datos para mejorar el rendimiento
    def cargar_datos(ruta):
        return pd.read_excel(ruta)

    df = cargar_datos('data/data.xlsx')

    st.write("""
    Comencemos visualizando algunos gráficos estadisticos referentes a la actividad pesquera de la zona
    """)

    # Agrupar por especie y aparejo, sumando los kilos
    df_agrupado_kilos = df.groupby(['Especie', 'Aparejo'])['Volumen_Kg'].sum().unstack()

    # Ordenar los datos por la suma total de kilos para cada especie (de menor a mayor)
    df_agrupado_kilos = df_agrupado_kilos.loc[df_agrupado_kilos.sum(axis=1).sort_values().index]

    # Seleccionar el tipo de gráfico para los kilos
    opcion_kilos = st.radio("Selecciona el tipo de gráfico para visualizar la distribución de la captura", ('Escala Normal', 'Escala Logarítmica'), key='kilos')

    # Crear el gráfico interactivo con Plotly
    if opcion_kilos == 'Escala Normal':
        st.subheader('Captura total por especie')
        fig = px.bar(df_agrupado_kilos, 
                    title='Captura total por especie',
                    labels={'value': 'Kilos', 'index': 'Especie'},
                    text_auto=True)
        fig.update_layout(yaxis_title='Kilos', xaxis_title='Especie', xaxis_tickangle=-45)
    else:
        st.subheader('Captura total por especie (Escala Logarítmica)')
        fig = px.bar(df_agrupado_kilos, 
                    title='Captura total por especie (Escala Logarítmica)',
                    labels={'value': 'Kilos', 'index': 'Especie'},
                    log_y=True,
                    text_auto=True)
        fig.update_layout(yaxis_title='Kilos (Logarítmico)', xaxis_title='Especie', xaxis_tickangle=-45)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Agrupar los datos por 'Especie' y sumar las ganancias
    ventas_por_especie = df.groupby('Especie')['Ganancia'].sum().sort_values()

    # Convertir el resultado en un DataFrame para Plotly
    df_ventas = ventas_por_especie.reset_index()
    df_ventas.columns = ['Especie', 'Ganancia']

    # Seleccionar el tipo de gráfico para las ganancias
    opcion_ganancia = st.radio("Selecciona el tipo de gráfico para visualizar las ganancias según la especie", ('Escala Normal', 'Escala Logarítmica'), key='escala_ganancia')

    # Crear el gráfico interactivo con Plotly
    if opcion_ganancia == 'Escala Normal':
        fig = px.bar(df_ventas, 
                    x='Especie', 
                    y='Ganancia', 
                    title='Ganancia por Especie (Escala Normal)', 
                    labels={'Ganancia': 'Ganancia (Suma Total)', 'Especie': 'Especie'},
                    color='Ganancia',
                    text='Ganancia')
        fig.update_layout(xaxis_title='Especie', yaxis_title='Ganancia (Suma Total)', xaxis_tickangle=-45)
    else:
        fig = px.bar(df_ventas, 
                    x='Especie', 
                    y='Ganancia', 
                    title='Ganancia por Especie (Escala Logarítmica)', 
                    labels={'Ganancia': 'Ganancia (Suma Total)', 'Especie': 'Especie'},
                    color='Ganancia',
                    text='Ganancia',
                    log_y=True)
        fig.update_layout(xaxis_title='Especie', yaxis_title='Ganancia (Suma Total) (Logarítmica)', xaxis_tickangle=-45)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Selección de la especie
    especie_seleccionada = st.selectbox('Selecciona la especie', df['Especie'].unique())

    # Filtrar los datos según la especie seleccionada
    df_filtrado = df[df['Especie'] == especie_seleccionada]

    # Crear dos columnas para centrar el mapa
    col1, col2, col3 = st.columns([1, 2, 1])  # Distribución de ancho: 1/4, 2/4, 1/4

    with col1:
        st.write("")  # Espacio vacío para centrar

    with col2:
        if not df_filtrado.empty:
            # Calcular la media de latitud y longitud para centrar el mapa
            media_lat = df_filtrado['Origen_Latitud'].mean()
            media_lon = df_filtrado['Origen_Longuitud'].mean()  # Asegúrate de que el nombre de la columna es correcto

            # Crear el mapa centrado en la ubicación media
            mapa = folium.Map(location=[media_lat, media_lon], zoom_start=6)

            # Opcional: Usar MarkerCluster para mejorar la visualización con muchos marcadores
            marker_cluster = MarkerCluster().add_to(mapa)

            # Añadir marcadores al cluster
            for idx, row in df_filtrado.iterrows():
                folium.Marker(
                    location=[row['Origen_Latitud'], row['Origen_Longuitud']],
                    popup=row['Origen']
                ).add_to(marker_cluster)

            # Mostrar el mapa en Streamlit
            folium_static(mapa, width=700, height=500)  # Ajusta el tamaño según tus necesidades
        else:
            st.warning("No se encontraron datos para la especie seleccionada.")

    with col3:
        st.write("")  # Espacio vacío para centrar

    precio_kg = df['Precio_Kg']
    talla_cm = df['Talla_cm']
    millas_recorridas = df['Millas_Recorridas']

    # Función para calcular el número óptimo de bins
    def calcular_bins(data, metodo):
        n = len(data)
        
        if metodo == "Sturges":
            return int(np.ceil(np.log2(n) + 1))
        
        elif metodo == "Freedman-Diaconis":
            q75, q25 = np.percentile(data, [75 ,25])
            iqr = q75 - q25
            bin_width_fd = 2 * iqr / np.cbrt(n)
            return int(np.ceil((data.max() - data.min()) / bin_width_fd))

    # Radio button para seleccionar el método de bins
    metodo = st.radio(
        "Selecciona el método para calcular el número de bins:",
        ("Sturges", "Freedman-Diaconis")
    )

    # Mostrar la fórmula dependiendo del método seleccionado
    if metodo == "Sturges":
        st.latex(r'''
            \text{Número de bins} = \lceil \log_2(n) + 1 \rceil
        ''')
    elif metodo == "Freedman-Diaconis":
        st.latex(r'''
            \text{Tamaño del bin} = \frac{2 \times IQR}{n^{1/3}}
        ''')

    # Calcular el número óptimo de bins para Precio_Kg
    optimo_bins_precio = calcular_bins(precio_kg, metodo)

    # Calcular el número óptimo de bins para Talla_cm
    optimo_bins_talla = calcular_bins(talla_cm, metodo)

    # Calcular el número óptimo de bins para Millas_Recorridas
    optimo_bins_millas = calcular_bins(millas_recorridas, metodo)


    # --- Gráfico para Precio por Kg ponderada por Volumen ---

    # Crear el histograma ponderado con el número óptimo de bins
    fig = px.histogram(df, x='Precio_Kg', y='Volumen_Kg', 
                    histfunc='sum', 
                    nbins=optimo_bins_precio,  # Usamos el número óptimo de bins
                    title='Distribución de Precio por Kg ponderada por Volumen en Kg')

    # Ajustar manualmente el inicio del bin
    bin_size_precio = (df['Precio_Kg'].max() - 0.5) / optimo_bins_precio  # Tamaño del bin según el número óptimo
    fig.update_traces(xbins=dict(
        start=0.5,  # Inicia desde 0.5
        end=df['Precio_Kg'].max(),  # Termina en el valor máximo de Precio_Kg
        size=bin_size_precio  # Tamaño del bin ajustado
    ))

    # Actualizar etiquetas del gráfico
    fig.update_layout(xaxis_title='Precio por Kg', 
                    yaxis_title='Volumen en Kg', 
                    bargap=0.1)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)


    # --- Gráfico para Talla en cm ponderada por Volumen ---

    st.title('Distribución de Precio por Kg ponderada por Talla en cm')

    # Crear el histograma ponderado con el número óptimo de bins
    fig = px.histogram(df, x='Talla_cm', y='Volumen_Kg', 
                    histfunc='sum', 
                    nbins=optimo_bins_talla,  # Usamos el número óptimo de bins
                    title='Distribución de Precio por Kg ponderada por Talla en cm')

    # Ajustar manualmente el inicio del bin
    bin_size_talla = (df['Talla_cm'].max() - df['Talla_cm'].min()) / optimo_bins_talla
    fig.update_traces(xbins=dict(
        start=df['Talla_cm'].min(),  # Inicia desde el valor mínimo de Talla
        end=df['Talla_cm'].max(),  # Termina en el valor máximo de Talla
        size=bin_size_talla  # Tamaño del bin ajustado
    ))

    # Actualizar etiquetas del gráfico
    fig.update_layout(xaxis_title='Talla en cm', 
                    yaxis_title='Volumen en Kg', 
                    bargap=0.1)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)


    # --- Gráfico para Millas Recorridas ponderada por Volumen ---

    st.title('Distribución de Precio por Kg ponderada por Millas Recorridas')

    # Crear el histograma ponderado con el número óptimo de bins
    fig = px.histogram(df, x='Millas_Recorridas', y='Volumen_Kg', 
                    histfunc='sum', 
                    nbins=optimo_bins_millas,  # Usamos el número óptimo de bins
                    title='Distribución de Precio por Kg ponderada por Millas Recorridas')

    # Ajustar manualmente el inicio del bin
    bin_size_millas = (df['Millas_Recorridas'].max() - df['Millas_Recorridas'].min()) / optimo_bins_millas
    fig.update_traces(xbins=dict(
        start=df['Millas_Recorridas'].min(),  # Inicia desde el valor mínimo de Millas Recorridas
        end=df['Millas_Recorridas'].max(),  # Termina en el valor máximo de Millas Recorridas
        size=bin_size_millas  # Tamaño del bin ajustado
    ))

    # Actualizar etiquetas del gráfico
    fig.update_layout(xaxis_title='Millas Recorridas', 
                    yaxis_title='Volumen en Kg', 
                    bargap=0.1)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Agrupar por Marca de Motor y Caballos de fuerza, sumando los kilos
    df_agrupado = df.groupby(['Marca_Motor', 'Caballos_Motor'])['Volumen_Kg'].sum().unstack()

    # Convertir el DataFrame a formato largo para Plotly
    df_agrupado_long = df_agrupado.reset_index().melt(id_vars='Marca_Motor', var_name='Caballos_Motor', value_name='Volumen_Kg')

    # Crear el selector de gráficos
    opcion = st.radio('Selecciona el tipo de gráfico para captura por caballos de motor:', ['Escala Normal', 'Escala Logarítmica'])

    # Crear el gráfico interactivo con Plotly
    if opcion == 'Escala Normal':
        st.subheader('Captura total por caballos de motor')
        fig = px.bar(df_agrupado_long, 
                    x='Marca_Motor', 
                    y='Volumen_Kg', 
                    color='Caballos_Motor', 
                    title='Captura total por Motor y Caballos de fuerza',
                    labels={'Marca_Motor': 'Motor', 'Volumen_Kg': 'Kilos'},
                    color_continuous_scale='viridis',
                    text='Volumen_Kg')
        fig.update_layout(xaxis_title='Motor', yaxis_title='Kilos', xaxis_tickangle=-45)
    else:
        st.subheader('Captura total por caballos de motor (Escala Logarítmica)')
        fig = px.bar(df_agrupado_long, 
                    x='Marca_Motor', 
                    y='Volumen_Kg', 
                    color='Caballos_Motor', 
                    title='Captura total por caballos de motor (Escala Logarítmica)',
                    labels={'Marca_Motor': 'Motor', 'Volumen_Kg': 'Kilos'},
                    color_continuous_scale='viridis',
                    text='Volumen_Kg',
                    log_y=True)
        fig.update_layout(xaxis_title='Motor', yaxis_title='Kilos (Logarítmico)', xaxis_tickangle=-45)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Agrupar los datos
    ventas_por_embarcacion = df.groupby('Embarcacion')['Ganancia'].sum()
    millas_por_embarcacion = df.groupby('Embarcacion')['Millas_Recorridas'].sum()
    volumen_por_embarcacion = df.groupby('Embarcacion')['Volumen_Kg'].sum()

    # Crear un DataFrame combinado
    datos_combinados = pd.DataFrame({
        'Ganancia': ventas_por_embarcacion,
        'Millas Recorridas': millas_por_embarcacion,
        'Volumen de Capturas': volumen_por_embarcacion
    })

    # Convertir el DataFrame combinado a formato largo para Plotly
    datos_combinados_long = datos_combinados.reset_index().melt(id_vars='Embarcacion', var_name='Métrica', value_name='Valor')

    # Crear botones para seleccionar el gráfico
    opcion = st.radio('Selecciona el tipo de gráfico:', 
                    ['Ganancia por Embarcación', 
                    'Millas Recorridas por Embarcación', 
                    'Volumen de Capturas por Embarcación',
                    'Barras Apiladas: Ganancia, Millas, Volumen'])

    # Mostrar el gráfico correspondiente
    if opcion == 'Ganancia por Embarcación':
        st.subheader('Ganancia por Embarcación')
        fig = px.bar(ventas_por_embarcacion.reset_index(), 
                    x='Embarcacion', 
                    y='Ganancia', 
                    title='Ganancia por Embarcación',
                    labels={'Ganancia': 'Ganancia', 'Embarcacion': 'Embarcación'},
                    color='Ganancia',
                    text='Ganancia')
        fig.update_layout(xaxis_title='Embarcación', yaxis_title='Ganancia', xaxis_tickangle=-45)

    elif opcion == 'Millas Recorridas por Embarcación':
        st.subheader('Millas Recorridas por Embarcación')
        fig = px.bar(millas_por_embarcacion.reset_index(), 
                    x='Embarcacion', 
                    y='Millas_Recorridas', 
                    title='Millas Recorridas por Embarcación',
                    labels={'Millas_Recorridas': 'Millas Recorridas', 'Embarcacion': 'Embarcación'},
                    color='Millas_Recorridas',
                    text='Millas_Recorridas')
        fig.update_layout(xaxis_title='Embarcación', yaxis_title='Millas Recorridas', xaxis_tickangle=-45)

    elif opcion == 'Volumen de Capturas por Embarcación':
        st.subheader('Volumen de Capturas por Embarcación')
        fig = px.bar(volumen_por_embarcacion.reset_index(), 
                    x='Embarcacion', 
                    y='Volumen_Kg', 
                    title='Volumen de Capturas por Embarcación',
                    labels={'Volumen_Kg': 'Volumen (Kg)', 'Embarcacion': 'Embarcación'},
                    color='Volumen_Kg',
                    text='Volumen_Kg')
        fig.update_layout(xaxis_title='Embarcación', yaxis_title='Volumen (Kg)', xaxis_tickangle=-45)

    elif opcion == 'Barras Apiladas: Ganancia, Millas, Volumen':
        st.subheader('Barras Apiladas: Ganancia, Millas, Volumen por Embarcación')
        fig = px.bar(datos_combinados_long, 
                    x='Embarcacion', 
                    y='Valor', 
                    color='Métrica', 
                    title='Barras Apiladas: Ganancia, Millas, Volumen por Embarcación',
                    labels={'Valor': 'Valores', 'Embarcacion': 'Embarcación'},
                    text='Valor')
        fig.update_layout(xaxis_title='Embarcación', yaxis_title='Valores', xaxis_tickangle=-45)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Agrupar las ganancias por fecha de faena
    df_agrupado = df.groupby('Inicio_Faena')['Ganancia'].sum().reset_index()

    # Crear el gráfico interactivo con Plotly
    st.subheader('Distribución de ganancias por Fecha de Faena')
    fig = px.line(df_agrupado, 
                x='Inicio_Faena', 
                y='Ganancia', 
                title='Distribución de Ganancias por Fecha de Faena',
                labels={'Inicio_Faena': 'Fecha de Faena', 'Ganancia': 'Ganancia'},
                markers=True)

    # Personalizar el gráfico
    fig.update_layout(xaxis_title='Fecha de Faena', yaxis_title='Ganancia', xaxis_tickformat='%Y-%m-%d')

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Agrupar las ganancias por fecha de faena
    df_agrupado = df.groupby('Inicio_Faena')['Costo_Combustible'].sum().reset_index()

    # Crear el gráfico interactivo con Plotly
    st.subheader('Distribución de Costo Combustible por Fecha de Faena')
    fig = px.line(df_agrupado, 
                x='Inicio_Faena', 
                y='Costo_Combustible', 
                title='Distribución de Costo Combustible por Fecha de Faena',
                labels={'Inicio_Faena': 'Fecha de Faena', 'Costo_Combustible': 'Costo_Combustible'},
                markers=True)

    # Personalizar el gráfico
    fig.update_layout(xaxis_title='Fecha de Faena', yaxis_title='Costo Combustible', xaxis_tickformat='%Y-%m-%d')

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Convertir la columna 'Inicio_Faena' y 'Fecha_Venta' a datetime
    df['Inicio_Faena'] = pd.to_datetime(df['Inicio_Faena'], format='%d %m %Y %H:%M')
    df['Inicio_Venta'] = pd.to_datetime(df['Inicio_Venta'], format='%d %m %Y %H:%M')

    # Transformar las columnas 'Inicio_Faena' y 'Inicio_Venta' en valores flotantes (hora + minutos/60)
    df['HFloat_Faena'] = df['Inicio_Faena'].dt.hour + df['Inicio_Faena'].dt.minute / 60
    df['HFloat_Venta'] = df['Inicio_Venta'].dt.hour + df['Inicio_Venta'].dt.minute / 60

    # Función para categorizar la hora en intervalos de 2 horas considerando A.M. y P.M.
    def categorize_hour(hour):
        period = "A.M." if hour < 12 else "P.M."
        hour_12 = hour % 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        start_hour = hour_12
        end_hour = (hour_12 + 2) % 12
        end_hour = 12 if end_hour == 0 else end_hour
        return f"{start_hour:02d} - {end_hour:02d} {period}"

    # Aplicar la función para categorizar las horas en 'Inicio_Faena' y 'Inicio_Venta'
    df['Hora_Faena'] = df['Inicio_Faena'].dt.hour.apply(categorize_hour)

    # Extraer el mes de las columnas 'Inicio_Faena' y 'Inicio_Venta'
    df['Mes_Faena'] = df['Inicio_Faena'].dt.month

    # Crear un diccionario para mapear los números de los meses a nombres abreviados
    meses = {
        1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR', 5: 'MAY', 6: 'JUN',
        7: 'JUL', 8: 'AGO', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC'
    }

    # Crear una nueva columna 'Mes_Faena' basada en el mes de 'Inicio_Faena' y usar el diccionario de mapeo
    df['Mes_Float'] = df['Inicio_Faena'].dt.month.map(meses)

    # Definir los límites de los rangos
    bins_precio = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
    # Definir las etiquetas correspondientes para cada rango
    labels_precio = ["S/ (0 - 5)", "S/ (5 - 10)", "S/ (10 - 15)", "S/ (15 - 20)", "S/ (20 - 25)",
            "S/ (25 - 30)", "S/ (30 - 35)", "S/ (35 - 40)", "S/ (40 - 45)", "S/ (45 - 50)", "S/ (50 - 55)"]

    # Crear la nueva columna 'Precio_Float'
    df['Precio_Float'] = pd.cut(df['Precio_Kg'], bins=bins_precio, labels=labels_precio, right=False)

    # Definir los límites de los rangos
    bins_talla = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    # Definir las etiquetas correspondientes para cada rango
    labels_talla = ["(10 - 20) cm", "(20 - 30) cm", "(30 - 40) cm", "(40 - 50) cm",
                    "(50 - 60) cm", "(60 - 70) cm", "(70 - 80) cm", "(80 - 90) cm", "(90 - 100) cm",
                    "(100 - 110) cm", "(110 - 120) cm", "(120 - 130) cm", "(130 - 140) cm", "(140 - 150) cm"]

    # Gráficos Estadísticos Descriptivos
    st.write("### Análisis Estadístico Descriptivo")

    # Selección de variables para el análisis
    numerical_columns = ['Temperatura_Agua_°C', 'Profundidad_m', 'Salinidad_PSU',
                        'Velocidad_Viento_m_s', 'Corriente_Marina_m_s', 'CPUE',
                        'Caballos_Motor', 'Millas_Recorridas', 'Precio_Kg',
                        'Talla_cm', 'Costo_Combustible', 'Ganancia']

    selected_var = st.multiselect("Selecciona las variables para visualizar", numerical_columns, default=numerical_columns[:3])

    # Selección del tipo de gráfico
    plot_type = st.selectbox("Selecciona el tipo de gráfico", ["Histograma", "Barra", "Boxplot", "Scatter"])

    # Selección de escala
    scale_option = st.selectbox("Selecciona la escala del eje Y", ["Lineal", "Logarítmica"])

    # Función para generar gráficos
    def generar_grafico(var, tipo, escala):
        if tipo == "Histograma":
            fig = px.histogram(df, x=var, nbins=30, title=f'Histograma de {var}')
        elif tipo == "Barra":
            fig = px.bar(df, x=var, title=f'Barra de {var}')
        elif tipo == "Boxplot":
            fig = px.box(df, y=var, title=f'Boxplot de {var}')
        elif tipo == "Scatter":
            # Si se selecciona scatter, pedir otra variable
            var_y = st.selectbox(f"Selecciona la variable Y para {var}", numerical_columns, index=1)
            fig = px.scatter(df, x=var, y=var_y, title=f'Scatter de {var} vs {var_y}')
        else:
            fig = {}
        
        if escala == "Logarítmica":
            fig.update_yaxes(type='log')
        
        return fig

    # Generar y mostrar gráficos
    for var in selected_var:
        fig = generar_grafico(var, plot_type, scale_option)
        st.plotly_chart(fig, use_container_width=True)

    # Gráficos de Tendencia
    st.write("### Gráficos de Tendencia")
    st.markdown("Selecciona una variable para ver su tendencia a lo largo del tiempo.")

    # Selección de variable para tendencia
    trend_var = st.selectbox("Selecciona la variable para la tendencia", numerical_columns, index=0)

    # Asegurarse de que 'Inicio_Faena' esté ordenado
    df_sorted = df.sort_values('Inicio_Faena')

    # Crear gráfico de tendencia
    fig_trend = px.line(df_sorted, x='Inicio_Faena', y=trend_var, title=f'Tendencia de {trend_var} a lo largo del tiempo')
    st.plotly_chart(fig_trend, use_container_width=True)

    # Gráfico de Dispersión Interactivo
    st.write("### Gráfico de Dispersión Interactivo")
    st.markdown("Selecciona las variables para los ejes y una opción para colorear los puntos.")

    # Selección de variables para el gráfico de dispersión
    scatter_x = st.selectbox("Selecciona la variable para el eje X", numerical_columns, index=0)
    scatter_y = st.selectbox("Selecciona la variable para el eje Y", numerical_columns, index=1)

    # Opcional: Selección de una variable para colorear
    color_option = st.selectbox("Selecciona una variable para colorear los puntos (opcional)", 
                                ["Ninguna"] + numerical_columns + ['Especie', 'Embarcacion'], index=0)

    # Crear el gráfico de dispersión
    if color_option != "Ninguna":
        fig_scatter = px.scatter(df, x=scatter_x, y=scatter_y, color=color_option,
                                title=f'Gráfico de Dispersión: {scatter_x} vs {scatter_y}',
                                hover_data=['Especie', 'Embarcacion'])
    else:
        fig_scatter = px.scatter(df, x=scatter_x, y=scatter_y,
                                title=f'Gráfico de Dispersión: {scatter_x} vs {scatter_y}',
                                hover_data=['Especie', 'Embarcacion'])

    # Mostrar el gráfico
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Crear la nueva columna 'Talla_Float'
    df['Talla_Float'] = pd.cut(df['Talla_cm'], bins=bins_talla, labels=labels_talla, right=False)

    # Crear un nuevo DataFrame eliminando las columnas datatime
    df_ = df.drop(columns=['Inicio_Faena', 'Inicio_Venta'])

    # Vista previa de los datos con nuevas columnas
    st.write("### Vista previa de los datos")
    st.write(df_.head())
    
    # Seleccionamos las columnas numéricas
    numeric_columns = df_.select_dtypes(include=['int64', 'float64', 'int32']).columns

    # Crear el escalador
    scaler = MinMaxScaler()

    # Aplicar la normalización
    df_normalized = df_.copy()
    df_normalized[numeric_columns] = scaler.fit_transform(df_[numeric_columns])

    st.write("### Datos normalizados")
    st.write(df_normalized.head())

    # --- Distribución de las faenas ---
    st.subheader('Distribución de las Faenas por Hora del Día')

    # Radio button para seleccionar el método de bins para Faenas
    metodo_faenas = st.radio(
        "Selecciona el método para calcular el número de bins en las faenas:",
        ("Sturges", "Freedman-Diaconis"),
        key="faenas_bins"
    )

    # Mostrar la fórmula dependiendo del método seleccionado
    if metodo_faenas == "Sturges":
        st.latex(r'''
            \text{Número de bins} = \lceil \log_2(n) + 1 \rceil
        ''')
    else:
        st.latex(r'''
            \text{Tamaño del bin} = \frac{2 \times IQR}{n^{1/3}}
        ''')

    # Calcular los bins para la distribución de faenas
    optimo_bins_faena = calcular_bins(df['HFloat_Faena'], metodo_faenas)

    # Crear el histograma interactivo con Plotly
    fig_faenas = px.histogram(df, x='HFloat_Faena', y='Volumen_Kg', 
                            nbins=optimo_bins_faena, 
                            title='Distribución de las Faenas por Hora del Día',
                            labels={'HFloat_Faena': 'Hora del Día', 'Volumen_Kg': 'Distribución de las Faenas'},
                            marginal="rug")

    # Actualizar el diseño del gráfico
    fig_faenas.update_layout(
        xaxis_title='Hora del Día',
        yaxis_title='Distribución de las Faenas',
        bargap=0.1
    )

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig_faenas, use_container_width=True)

    # --- Distribución de las ventas ---
    st.subheader('Distribución de las Ventas por Hora del Día')

    # Radio button para seleccionar el método de bins para Ventas
    metodo_ventas = st.radio(
        "Selecciona el método para calcular el número de bins en las ventas:",
        ("Sturges", "Freedman-Diaconis"),
        key="ventas_bins"
    )

    # Mostrar la fórmula dependiendo del método seleccionado
    if metodo_ventas == "Sturges":
        st.latex(r'''
            \text{Número de bins} = \lceil \log_2(n) + 1 \rceil
        ''')
    else:
        st.latex(r'''
            \text{Tamaño del bin} = \frac{2 \times IQR}{n^{1/3}}
        ''')

    # Calcular los bins para la distribución de ventas
    optimo_bins_venta = calcular_bins(df['HFloat_Venta'], metodo_ventas)

    # Crear el histograma interactivo con Plotly
    fig_ventas = px.histogram(df, x='HFloat_Venta', y='Venta', 
                            nbins=optimo_bins_venta, 
                            title='Distribución de las Ventas por Hora del Día',
                            labels={'HFloat_Venta': 'Hora del Día', 'Venta': 'Distribución de las Ventas'},
                            marginal="rug")

    # Actualizar el diseño del gráfico
    fig_ventas.update_layout(
        xaxis_title='Hora del Día',
        yaxis_title='Distribución de las Ventas',
        bargap=0.1
    )

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig_ventas, use_container_width=True)

    # Matriz de Correlación
    st.write("### Matriz de Correlación entre Variables")
    st.markdown("Visualiza las correlaciones lineales entre las variables numéricas seleccionadas.")

    # Selección de variables para la matriz de correlación
    corr_variables = st.multiselect(
        "Selecciona las variables para incluir en la matriz de correlación",
        options=numerical_columns,
        default=numerical_columns
    )

    # Calcular la matriz de correlación
    if corr_variables:
        corr_matrix = df[corr_variables].corr(method='pearson')
        
        # Crear el mapa de calor interactivo usando Plotly
        fig_corr = px.imshow(corr_matrix,
                            text_auto=True,
                            aspect="auto",
                            color_continuous_scale='RdBu_r',
                            title='Matriz de Correlación de Pearson')
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Opcional: Descargar la matriz de correlación
        csv_corr = corr_matrix.to_csv(index=True).encode('utf-8')
        st.download_button(
            label="Descargar Matriz de Correlación como CSV",
            data=csv_corr,
            file_name='matriz_correlacion.csv',
            mime='text/csv',
        )
    else:
        st.warning("Por favor, selecciona al menos una variable para mostrar la matriz de correlación.")
