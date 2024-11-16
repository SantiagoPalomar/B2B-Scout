import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import psycopg2
from config import get_db_config

#Conexion a la base de datos
def conectar_db():
    config = get_db_config()
    print(config)  # Esto mostrará todas las claves y valores en el diccionario
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password'],
        sslmode='require'  # Usa SSL si es necesario
    )
    return conn

#Obtener los datos de la tabla empresas
def obtener_datos():
    conn = conectar_db()
    query = "SELECT * FROM empresas"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Título de la aplicación
st.title("B2B SCOUT")

# Ruta de la imagen
logo_path = "Logo_B2B.png" 

# Mostrar la imagen
st.image(logo_path, caption="Mi Logo B2B", use_column_width=True)

data_db = obtener_datos()

# Crear el menú de navegación en la barra lateral
opciones = st.sidebar.radio("Selecciona una opción:", ["Ver Proveedores", "Comparación de Proveedores"])


# Página "Ver Proveedores"
if opciones == "Ver Proveedores":
    search_term = st.text_input("Buscar proveedor...")
    
    data_db = obtener_datos()

    # Filtrar los proveedores según el término de búsqueda
    filtered_df = data_db[data_db["razon_social"].str.contains(search_term, case=False)] if search_term else data_db

    if not filtered_df.empty:
        
        data_db = obtener_datos()
        # Calcular métricas adicionales para 2021
        filtered_df['Razón de Endeudamiento 2021'] = filtered_df['total_pasivos_2021'] / filtered_df['total_activos_2021']
        filtered_df['Rentabilidad 2021'] = filtered_df['ganancia_perdida_2021'] / filtered_df['ingresos_operacionales_2021']
        filtered_df['Solvencia 2021'] = filtered_df['total_patrimonio_2021'] / filtered_df['total_pasivos_2021']

        # Calcular métricas adicionales para 2020
        filtered_df['Razón de Endeudamiento 2020'] = filtered_df['total_pasivos_2020'] / filtered_df['total_activos_2020']
        filtered_df['Rentabilidad 2020'] = filtered_df['ganancia_perdida_2020'] / filtered_df['ingresos_operacionales_2020']
        filtered_df['Solvencia 2020'] = filtered_df['total_patrimonio_2020'] / filtered_df['total_pasivos_2020']

        # Mostrar tabla de proveedores
        st.subheader("Lista de Proveedores")
        st.dataframe(filtered_df)

        # Gráfico comparativo de métricas
        metrics = ['Razón de Endeudamiento', ' Rentabilidad', 'Solvencia']
        values_2021 = [
            filtered_df['Razón de Endeudamiento 2021'].mean() * 100,
            filtered_df['Rentabilidad 2021'].mean() * 100,
            filtered_df['Solvencia 2021'].mean() * 100
        ]
        values_2020 = [
            filtered_df['Razón de Endeudamiento 2020'].mean() * 100,
            filtered_df['Rentabilidad 2020'].mean() * 100,
            filtered_df['Solvencia 2020'].mean() * 100
        ]

        fig = go.Figure(data=[
            go.Bar(name='2020', x=metrics, y=values_2020, marker_color='#4CAF50'),
            go.Bar(name='2021', x=metrics, y=values_2021, marker_color='#2196F3')
        ])
        fig.update_layout(title='Comparación de Indicadores Clave (2020 vs 2021)', 
                        xaxis_title='Métricas', 
                        yaxis_title='Valores (%)',
                        barmode='group')
        st.plotly_chart(fig)

        # Geocodificación de las ciudades y mapa
        geolocator = Nominatim(user_agent="mi_aplicacion_simulada")
        geocoded_data = []

        for _, row in filtered_df.iterrows():
            location = geolocator.geocode(row['ciudad_domicilio'])
            if location:
                geocoded_data.append({
                    'razon_social': row['razon_social'],
                    'lat': location.latitude,
                    'lon': location.longitude
                })

        if geocoded_data:
            df_geocoded = pd.DataFrame(geocoded_data)
            st.subheader("Ubicación de Proveedores en Colombia")
            st.map(df_geocoded[['lat', 'lon']])
        else:
            st.warning("No se pudieron geocodificar las ciudades.")

# Página "Comparación de Proveedores"
elif opciones == "Comparación de Proveedores":

    st.subheader("Comparación de Proveedores")

    col1, col2 = st.columns(2)

    with col1:
        proveedor1 = st.selectbox("Seleccionar primer proveedor", data_db["razon_social"], key="proveedor1")
    with col2:
        proveedor2 = st.selectbox("Seleccionar segundo proveedor", data_db["razon_social"], key="proveedor2")
    if proveedor1 and proveedor2:
        datos_proveedor1 = data_db[data_db["razon_social"] == proveedor1].iloc[0]
        datos_proveedor2 = data_db[data_db["razon_social"] == proveedor2].iloc[0]

        # Calcular métricas para los proveedores seleccionados
        razon_endeudamiento1 = datos_proveedor1['total_pasivos_2021'] / datos_proveedor1['total_activos_2021'] * 100
        rentabilidad1 = datos_proveedor1['ganancia_perdida_2021'] / datos_proveedor1['ingresos_operacionales_2021'] * 100
        solvencia1 = datos_proveedor1['total_patrimonio_2021'] / datos_proveedor1['total_pasivos_2021'] * 100
        razon_endeudamiento2 = datos_proveedor2['total_pasivos_2021'] / datos_proveedor2['total_activos_2021'] * 100
        rentabilidad2 = datos_proveedor2['ganancia_perdida_2021'] / datos_proveedor2['ingresos_operacionales_2021'] * 100
        solvencia2 = datos_proveedor2['total_patrimonio_2021'] / datos_proveedor2['total_pasivos_2021'] * 100

        # Crear gráfico comparativo
        fig = go.Figure(data=[
            go.Bar(name=proveedor1, x=['Razón de Endeudamiento', 'Rentabilidad', 'Solvencia'], 
                y=[razon_endeudamiento1, rentabilidad1, solvencia1]),
            go.Bar(name=proveedor2, x=['Razón de Endeudamiento', 'Rentabilidad', 'Solvencia'], 
                y=[razon_endeudamiento2, rentabilidad2, solvencia2])
        ])
        fig.update_layout(title='Comparación de Indicadores', xaxis_title='Métricas', yaxis_title='Valores (%)')
        st.plotly_chart(fig)

        # Recomendaciones basadas en las métricas
        mejor_cumplimiento = data_db.loc[(data_db['ganancia_perdida_2021'] / data_db['ingresos_operacionales_2021']).idxmax()]
        menor_riesgo = data_db.loc[(data_db['total_pasivos_2021'] / data_db['total_activos_2021']).idxmin()]
        mas_sostenible = data_db.loc[(data_db['total_patrimonio_2021'] / data_db['total_pasivos_2021']).idxmax()]

        st.write(f"- Mejor cumplimiento: **{mejor_cumplimiento['razon_social']}** con {mejor_cumplimiento['ganancia_perdida_2021'] / mejor_cumplimiento['ingresos_operacionales_2021'] * 100:.2f}%")
        st.write(f"- Menor riesgo financiero: **{menor_riesgo['razon_social']}** con {menor_riesgo['total_pasivos_2021'] / menor_riesgo['total_activos_2021'] * 100:.2f}%")
        st.write(f"- Más sostenible: **{mas_sostenible['razon_social']}** con {mas_sostenible['total_patrimonio_2021'] / mas_sostenible['total_pasivos_2021'] * 100:.2f}%")

        st.write("\nConsideraciones:")
        st.write("- Evalúe la posibilidad de aumentar la colaboración con proveedores de alto cumplimiento.")
        st.write("- Considere diversificar para mitigar riesgos con proveedores de alto riesgo financiero.")
        st.write("- Explore oportunidades para mejorar la sostenibilidad en su cadena de suministro.")