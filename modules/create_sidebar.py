# modules/create_sidebar.py
import streamlit as st
from streamlit_option_menu import option_menu
from paginas import inicio, datos, eda, identificacion_modelo, modelo_predictivo

def create_sidebar():
    # Añadir texto personalizado en el sidebar con markdown y HTML
    st.sidebar.markdown(
        f'<div style="text-align: center; font-size: 18px; margin-bottom: 30px;">'
        f'Proyecto realizado por:<br>'
        f'APAZA PEREZ OSCAR GONZALO<br>'
        f'CABEZAS HUANIO RUBEN KELVIN<br>'
        f'RUIZ ALVA JERSON ENMANUEL<br>'
        f'PONCE DE LEON TORRES FABYOLA<br>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Crear el menú de opciones en el sidebar con option_menu
    with st.sidebar:
        selected = option_menu("Menú", ["Inicio", "Datos", "EDA", "Identificación del Modelo", "Modelo Predictivo"],
            icons=["house", "database", "bar-chart-line", "diagram-3", "graph-up-arrow"],
            menu_icon="cast", default_index=0, orientation="vertical")

    # Llama a la función de la página correspondiente en función de la selección
    if selected == "Inicio":
        inicio.display()
    elif selected == "Datos":
        datos.display()
    elif selected == "EDA":
        eda.display()
    elif selected == "Identificación del Modelo":
        identificacion_modelo.display()
    elif selected == "Modelo Predictivo":
        modelo_predictivo.display()
