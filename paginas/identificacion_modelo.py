# paginas/identificacion_modelo.py
# Importar librerías necesarias
import streamlit as st
import numpy as np
import pandas as pd
# Preprocesamiento
from sklearn.preprocessing import MinMaxScaler  # Normalización
from sklearn.preprocessing import OneHotEncoder  # Codificación
from sklearn.compose import ColumnTransformer
from sklearn.utils import resample  # Balanceo de datos
from imblearn.over_sampling import SMOTE  # Balanceo de datos
# Modelos
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
# Evaluación del modelo
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, confusion_matrix, accuracy_score, f1_score
# Gráficos
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import requests  # Para hacer solicitudes a la API

def display():
    # Configuración de la página
    st.markdown("<h2 style='text-align: center;'>Identificación del Modelo</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # Cargar los datos
    @st.cache_data
    def cargar_datos(ruta):
        return pd.read_excel(ruta)

    df = cargar_datos('data/data.xlsx')
    st.write("### Vista previa de los datos")
    st.write(df.head(30))

    # Obtener los tipos de datos de cada columna
    data_types = df.dtypes.reset_index()
    data_types.columns = ["Columna", "Tipo de dato"]

    # Mostrar los tipos de datos en múltiples columnas
    st.write("**Tipos de datos por columna:**")

    # Determinar el número de columnas que deseas (por ejemplo, 5)
    num_columns = 5

    # Dividir el DataFrame en partes iguales
    data_splits = np.array_split(data_types, num_columns)

    # Crear las columnas en Streamlit
    cols = st.columns(num_columns)

    # Iterar sobre cada segmento y cada columna para mostrar los datos
    for idx, (col, split) in enumerate(zip(cols, data_splits)):
        with col:
            for index, row in split.iterrows():
                st.write(f"**{row['Columna']}**: {row['Tipo de dato']}")

    # --- Matriz de Correlación ---
    st.write("### Matriz de Correlación entre Variables")
    st.markdown("Visualiza las correlaciones lineales entre las variables numéricas seleccionadas.")

    # Selección de variables para el análisis
    numerical_columns = ['Temperatura_Agua_°C', 'Profundidad_m', 'Salinidad_PSU',
                         'Velocidad_Viento_m_s', 'Corriente_Marina_m_s', 'CPUE',
                         'Caballos_Motor', 'Millas_Recorridas', 'Precio_Kg',
                         'Talla_cm', 'Costo_Combustible', 'Ganancia']

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
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title='Matriz de Correlación de Pearson'
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Opcional: Descargar la matriz de correlación
        csv_corr = corr_matrix.to_csv(index=True).encode('utf-8')
        st.download_button(
            label="Descargar Matriz de Correlación como CSV",
            data=csv_corr,
            file_name='matriz_correlacion.csv',
            mime='text/csv',
        )
        
        # --- Análisis de Correlaciones Significativas ---
        st.write("## Análisis de Correlaciones Significativas")

        # Añadir un slider para seleccionar el umbral de correlación
        threshold = st.slider(
            "Selecciona el umbral mínimo de correlación para considerar significativa",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05
        )

        # Desapilar la matriz de correlación para obtener pares de variables
        corr_pairs = corr_matrix.unstack()

        # Filtrar las correlaciones significativas
        significant_corr = corr_pairs[(abs(corr_pairs) >= threshold) & (abs(corr_pairs) < 1)].drop_duplicates().sort_values(ascending=False)

        # Mostrar las correlaciones significativas
        st.write(f"### Correlaciones significativas (|correlación| ≥ {threshold}):")
        if not significant_corr.empty:
            for (var1, var2), corr_value in significant_corr.items():
                st.write(f"- **{var1}** y **{var2}**: correlación de **{corr_value:.2f}**.")
        else:
            st.write("No se encontraron correlaciones significativas con el umbral seleccionado.")

    else:
        st.warning("Por favor, selecciona al menos una variable para mostrar la matriz de correlación.")

    # --- Transformaciones de Datos ---
    st.write("## Transformaciones de Datos")

    # Convertir las columnas 'Inicio_Faena' y 'Inicio_Venta' a datetime
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

    # Aplicar la función para categorizar las horas en 'Inicio_Faena'
    df['Hora_Faena'] = df['Inicio_Faena'].dt.hour.apply(categorize_hour)

    # Extraer el mes de 'Inicio_Faena' y mapear a nombres
    meses = {
        1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR', 5: 'MAY', 6: 'JUN',
        7: 'JUL', 8: 'AGO', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC'
    }
    df['Mes_Float'] = df['Inicio_Faena'].dt.month.map(meses)

    # Crear la nueva columna 'Precio_Float' categorizando 'Precio_Kg'
    bins_precio = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
    labels_precio = ["S/ (0 - 5)", "S/ (5 - 10)", "S/ (10 - 15)", "S/ (15 - 20)", "S/ (20 - 25)",
                     "S/ (25 - 30)", "S/ (30 - 35)", "S/ (35 - 40)", "S/ (40 - 45)", "S/ (45 - 50)", "S/ (50 - 55)"]
    df['Precio_Float'] = pd.cut(df['Precio_Kg'], bins=bins_precio, labels=labels_precio, right=False)

    # Crear la nueva columna 'Talla_Float' categorizando 'Talla_cm'
    bins_talla = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    labels_talla = ["(10 - 20) cm", "(20 - 30) cm", "(30 - 40) cm", "(40 - 50) cm",
                    "(50 - 60) cm", "(60 - 70) cm", "(70 - 80) cm", "(80 - 90) cm", "(90 - 100) cm",
                    "(100 - 110) cm", "(110 - 120) cm", "(120 - 130) cm", "(130 - 140) cm", "(140 - 150) cm"]
    df['Talla_Float'] = pd.cut(df['Talla_cm'], bins=bins_talla, labels=labels_talla, right=False)

    # Crear un nuevo DataFrame eliminando las columnas datetime
    df_ = df.drop(columns=['Inicio_Faena', 'Inicio_Venta'])

    # Mostrar descripción de las transformaciones
    st.write("""
    **Descripción de las transformaciones:**
    - Se convirtieron las fechas a formato datetime y se extrajeron componentes como hora y mes.
    - Se categorizaron las horas en intervalos de 2 horas con distinción entre A.M. y P.M.
    - Se categorizó el mes en nombres abreviados.
    - Se crearon categorías para los rangos de precios y tallas.
    """)

    # Vista previa de los datos con nuevas columnas
    st.write("### Datos después de las transformaciones")
    st.write(df_.head())

    # --- Selección de la Variable Objetivo ---
    st.write("## Selección de la Variable Objetivo")
    target_options = df_.columns.tolist()
    target_variable = st.selectbox("Selecciona la variable objetivo", options=target_options, index=target_options.index('Ganancia'))

    # Separar características y variable objetivo
    if target_variable in df_.columns:
        y = df_[target_variable]
        X = df_.drop(columns=[target_variable])
    else:
        st.error(f"La variable objetivo '{target_variable}' no se encuentra en los datos.")
        return

    # Identificar si es un problema de clasificación o regresión
    if y.dtype == 'object' or y.nunique() <= 10:
        problem_type = 'classification'
    else:
        problem_type = 'regression'

    st.write(f"El problema identificado es de **{problem_type}**.")

    # --- Preprocesamiento ---
    # Identificar columnas categóricas y numéricas
    categorical_columns = X.select_dtypes(include=['object']).columns.tolist()
    numerical_columns = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

    # Crear lista de transformadores
    transformers = []

    if numerical_columns:
        transformers.append(('num', MinMaxScaler(), numerical_columns))
    else:
        st.warning("No se encontraron columnas numéricas para escalar.")

    if categorical_columns:
        transformers.append(('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_columns))
    else:
        st.warning("No se encontraron columnas categóricas para codificar.")

    if not transformers:
        st.error("No hay columnas para transformar.")
        return

    # Crear el preprocesador con los transformadores disponibles
    preprocessor = ColumnTransformer(transformers=transformers)

    # Aplicar el preprocesador a X
    preprocessed_data = preprocessor.fit_transform(X)

    # Obtener los nombres de las características
    feature_names = []

    if numerical_columns:
        numerical_feature_names = numerical_columns
        feature_names.extend(numerical_feature_names)

    if categorical_columns:
        onehot_encoder = preprocessor.named_transformers_['cat']
        onehot_feature_names = onehot_encoder.get_feature_names_out(categorical_columns)
        feature_names.extend(onehot_feature_names)

    # Verificar que la longitud de feature_names coincide con el número de columnas en preprocessed_data
    if preprocessed_data.shape[1] != len(feature_names):
        st.error("El número de características no coincide con el número de columnas en los datos preprocesados.")
        return

    # Crear un DataFrame con los datos preprocesados
    preprocessed_df = pd.DataFrame(preprocessed_data, columns=feature_names)

    st.write("### Datos preprocesados")
    st.write(preprocessed_df.head())

    # --- Balanceo de Datos ---
    st.write("## Balanceo de Datos")
    if problem_type == 'classification':
        st.write("Verificando si es necesario balancear las clases...")

        class_counts = y.value_counts()
        st.write("Distribución de clases:")
        st.write(class_counts)

        if class_counts.min() / class_counts.max() < 0.5:
            st.write("Las clases están desbalanceadas. Aplicando técnicas de balanceo...")

            # Seleccionar técnica de balanceo
            balance_method = st.selectbox("Selecciona la técnica de balanceo", ["Submuestreo (Under-sampling)", "Sobremuestreo (Over-sampling)", "SMOTE"])

            if balance_method == "Submuestreo (Under-sampling)":
                # Implementar submuestreo
                df_balanced = pd.concat([
                    resample(df_[df_[target_variable] == class_counts.idxmin()],
                             replace=True,
                             n_samples=class_counts.max(),
                             random_state=42),
                    df_[df_[target_variable] == class_counts.idxmax()]
                ])
                y = df_balanced[target_variable]
                X = df_balanced.drop(columns=[target_variable])
            elif balance_method == "Sobremuestreo (Over-sampling)":
                # Implementar sobremuestreo
                df_balanced = pd.concat([
                    df_[df_[target_variable] == class_counts.idxmin()],
                    resample(df_[df_[target_variable] == class_counts.idxmax()],
                             replace=False,
                             n_samples=class_counts.min(),
                             random_state=42)
                ])
                y = df_balanced[target_variable]
                X = df_balanced.drop(columns=[target_variable])
            else:
                # Implementar SMOTE
                smote = SMOTE(random_state=42)
                X_resampled, y_resampled = smote.fit_resample(preprocessed_df, y)
                X = X_resampled
                y = y_resampled

            st.write("Distribución de clases después del balanceo:")
            st.write(y.value_counts())
        else:
            st.write("Las clases están balanceadas. No se aplicará balanceo.")
            X = preprocessed_df
    else:
        X = preprocessed_df

    # --- División de Datos ---
    st.write("## División del Conjunto de Datos")
    test_size = st.slider("Selecciona el tamaño del conjunto de prueba", min_value=0.1, max_value=0.5, value=0.2, step=0.05)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    st.write(f"Conjunto de entrenamiento: {X_train.shape[0]} muestras")
    st.write(f"Conjunto de prueba: {X_test.shape[0]} muestras")

    # --- Selección y Entrenamiento de Modelos ---
    if problem_type == 'regression':
        models = {
            'Regresión Lineal': LinearRegression(),
            'Árbol de Decisión': DecisionTreeRegressor(random_state=42),
            'Bosque Aleatorio': RandomForestRegressor(random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(random_state=42)
        }
        st.write("""
            En este análisis de regresión, utilizamos las siguientes métricas para evaluar el rendimiento de los modelos:

            - **Error Cuadrático Medio (MSE):** Mide la diferencia promedio al cuadrado entre los valores reales y los predichos. Un MSE más bajo indica mejores predicciones.
            """)
        st.latex(r'''
            MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2
            ''')
        st.write("""
            - **Coeficiente de Determinación (R²):** Indica la proporción de la variación en la variable dependiente que es explicada por el modelo. Un R² cercano a 1 indica un buen ajuste.
            """)
        st.latex(r'''
            R^2 = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}
            ''')
    else:
        models = {
            'Regresión Logística': LogisticRegression(max_iter=1000),
            'Árbol de Decisión': DecisionTreeClassifier(random_state=42),
            'Bosque Aleatorio': RandomForestClassifier(random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(random_state=42)
        }
        st.write("""
            En este análisis de clasificación, utilizamos las siguientes métricas para evaluar el rendimiento de los modelos:

            - **Exactitud (Accuracy):** Proporción de predicciones correctas realizadas por el modelo.
            """)
        st.latex(r'''
            Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
            ''')
        st.write("""
            - **F1 Score:** Media armónica de la precisión y la exhaustividad (recall), útil para datos desbalanceados.
            """)
        st.latex(r'''
            F1 = 2 \times \frac{Precisión \times Exhaustividad}{Precisión + Exhaustividad}
            ''')
            
    results = []

    for name, model in models.items():
        # Entrenar el modelo
        model.fit(X_train, y_train)
        # Predecir en el conjunto de prueba
        y_pred = model.predict(X_test)

    def generar_respuesta_rapidapi(prediccion, X_test, problem_type, model_name, metrics):
        import json

        # Construir el prompt con la predicción, los datos de entrada del usuario y el contexto del proyecto
        if problem_type == 'regression':
            prompt = f"""Como un experto en ciencia de datos especializado en el análisis de la pesca artesanal en Áncash, explica los resultados del modelo de regresión {model_name}. 
            Las predicciones de ganancias son: {prediccion[:5]} (mostrando 5 de {len(prediccion)}). 
            Métricas del modelo: MSE = {metrics['MSE']:.4f}, R² = {metrics['R2']:.4f}.
            Considera factores como el volumen de pesca, condiciones ambientales (temperatura del agua, salinidad, velocidad del viento), costos operativos (combustible) y precios de mercado.
            Explica cómo estos factores podrían influir en las ganancias predichas y qué implicaciones tienen estos resultados para los pescadores artesanales y las políticas pesqueras en Áncash.
            Utiliza un lenguaje claro y conciso para que un funcionario del gobierno local pueda entender los resultados y sus implicaciones."""
        else:
            prompt = f"""Como un experto en ciencia de datos especializado en el análisis de la pesca artesanal en Áncash, explica los resultados del modelo de clasificación {model_name}. 
            Las predicciones son: {prediccion[:5]} (mostrando 5 de {len(prediccion)}). 
            Métricas del modelo: Accuracy = {metrics['Accuracy']:.4f}, F1 Score = {metrics['F1 Score']:.4f}.
            Considera factores como el tipo de especie pescada, el aparejo utilizado, la zona de pesca y las condiciones ambientales.
            Explica cómo estos factores podrían influir en las clasificaciones predichas y qué implicaciones tienen estos resultados para la gestión sostenible de los recursos pesqueros en Áncash.
            Utiliza un lenguaje claro y conciso para que un funcionario del gobierno local pueda entender los resultados y sus implicaciones."""

        url = "https://cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com/v1/chat/completions"

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "gpt-4",
            "max_tokens": 500,
            "temperature": 0.7
        }

        headers = {
            "x-rapidapi-key": "rapidapi_key",
            "x-rapidapi-host": "cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except requests.RequestException as e:
            st.error(f"Error al comunicarse con la API: {e}")
            return "No se pudo generar la explicación."
        except Exception as e:
            st.error(f"Error inesperado: {e}")
            return "No se pudo generar la explicación."
        
    # --- Entrenamiento y Evaluación de Modelos ---
    st.write("## Entrenamiento y Evaluación de Modelos")

    results = []

    for name, model in models.items():
        st.write(f"### {name}")
        # Entrenar el modelo
        model.fit(X_train, y_train)
        # Predecir en el conjunto de prueba
        y_pred = model.predict(X_test)

        # Calcular métricas
        if problem_type == 'regression':
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            st.write(f"- **Error Cuadrático Medio (MSE):** {mse:.4f}")
            st.write(f"- **Coeficiente de Determinación (R²):** {r2:.4f}")
            results.append({'Modelo': name, 'MSE': mse, 'R2': r2})
            metrics = {'MSE': mse, 'R2': r2}
        else:
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            st.write(f"- **Exactitud (Accuracy):** {acc:.4f}")
            st.write(f"- **F1 Score:** {f1:.4f}")
            results.append({'Modelo': name, 'Accuracy': acc, 'F1 Score': f1})
            metrics = {'Accuracy': acc, 'F1 Score': f1}

        # Generar explicación usando la función generar_respuesta_rapidapi actualizada
        explicacion = generar_respuesta_rapidapi(y_pred, X_test, problem_type, name, metrics)
        st.write("#### Explicación de los Resultados")
        st.write(explicacion)

    # Convertir resultados a DataFrame
    results_df = pd.DataFrame(results)

    # Mostrar gráficos comparativos
    if problem_type == 'regression':
        fig_mse = px.bar(results_df, x='Modelo', y='MSE', title='Comparación de MSE entre Modelos')
        st.plotly_chart(fig_mse, use_container_width=True)
        fig_r2 = px.bar(results_df, x='Modelo', y='R2', title='Comparación de R² entre Modelos')
        st.plotly_chart(fig_r2, use_container_width=True)
    else:
        fig_acc = px.bar(results_df, x='Modelo', y='Accuracy', title='Comparación de Accuracy entre Modelos')
        st.plotly_chart(fig_acc, use_container_width=True)
        fig_f1 = px.bar(results_df, x='Modelo', y='F1 Score', title='Comparación de F1 Score entre Modelos')
        st.plotly_chart(fig_f1, use_container_width=True)

    st.write("""
    **Conclusión:**
    Basándonos en las métricas obtenidas, podemos identificar el modelo que mejor se ajusta a nuestros datos y considerarlo para futuras predicciones.
    """)
