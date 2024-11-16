import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

# Título de la aplicación
st.title("B2B SCOUT")

# Simulación de datos
data_simulada = pd.DataFrame({
    "NIT": ["123456789", "987654321", "543216789"],
    "RAZON_SOCIAL": ["Proveedor A", "Proveedor B", "Proveedor C"],
    "CIUDAD_DOMICILIO": ["Bogotá", "Medellín", "Cali"],
    "CIIU": ["6201", "6202", "6203"],
    "MACROSECTOR": ["Tecnología", "Construcción", "Manufactura"],
    "CONTACTO": ["contactoA@example.com", "contactoB@example.com", "contactoC@example.com"],
    "INGRESOS_OPERACIONALES_2021": [1000000, 2000000, 1500000],
    "GANANCIA_PERDIDA_2021": [200000, 300000, 250000],
    "TOTAL_ACTIVOS_2021": [500000, 700000, 600000],
    "TOTAL_PASIVOS_2021": [100000, 200000, 150000],
    "TOTAL_PATRIMONIO_2021": [400000, 500000, 450000],
    "GANANCIA_PERDIDA_2020": [150000, 250000, 200000],
    "INGRESOS_OPERACIONALES_2020": [900000, 1800000, 1400000],  # Asegúrate de incluir esto
    "TOTAL_ACTIVOS_2020": [450000, 650000, 550000],
    "TOTAL_PASIVOS_2020": [90000, 190000, 140000],
    "TOTAL_PATRIMONIO_2020": [360000, 460000, 410000]
})

# Crear el menú de navegación en la barra lateral
opciones = st.sidebar.radio("Selecciona una opción:", ["Ver Proveedores", "Comparación de Proveedores"])

# Página "Ver Proveedores"
if opciones == "Ver Proveedores":
    search_term = st.text_input("Buscar proveedor...")

    # Filtrar los proveedores según el término de búsqueda
    filtered_df = data_simulada[data_simulada["RAZON_SOCIAL"].str.contains(search_term, case=False)] if search_term else data_simulada

    if not filtered_df.empty:
        # Calcular métricas adicionales para 2021
        filtered_df['Razón de Endeudamiento 2021'] = filtered_df['TOTAL_PASIVOS_2021'] / filtered_df['TOTAL_ACTIVOS_2021']
        filtered_df['Rentabilidad 2021'] = filtered_df['GANANCIA_PERDIDA_2021'] / filtered_df['INGRESOS_OPERACIONALES_2021']
        filtered_df['Solvencia 2021'] = filtered_df['TOTAL_PATRIMONIO_2021'] / filtered_df['TOTAL_PASIVOS_2021']

        # Calcular métricas adicionales para 2020
        filtered_df['Razón de Endeudamiento 2020'] = filtered_df['TOTAL_PASIVOS_2020'] / filtered_df['TOTAL_ACTIVOS_2020']
        filtered_df['Rentabilidad 2020'] = filtered_df['GANANCIA_PERDIDA_2020'] / filtered_df['INGRESOS_OPERACIONALES_2020']
        filtered_df['Solvencia 2020'] = filtered_df['TOTAL_PATRIMONIO_2020'] / filtered_df['TOTAL_PASIVOS_2020']

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
            location = geolocator.geocode(row['CIUDAD_DOMICILIO'])
            if location:
                geocoded_data.append({
                    'RAZON_SOCIAL': row['RAZON_SOCIAL'],
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
        proveedor1 = st.selectbox("Seleccionar primer proveedor", data_simulada["RAZON_SOCIAL"], key="proveedor1")
    with col2:
        proveedor2 = st.selectbox("Seleccionar segundo proveedor", data_simulada["RAZON_SOCIAL"], key="proveedor2")
    if proveedor1 and proveedor2:
        datos_proveedor1 = data_simulada[data_simulada["RAZON_SOCIAL"] == proveedor1].iloc[0]
        datos_proveedor2 = data_simulada[data_simulada["RAZON_SOCIAL"] == proveedor2].iloc[0]

        # Calcular métricas para los proveedores seleccionados
        razon_endeudamiento1 = datos_proveedor1['TOTAL_PASIVOS_2021'] / datos_proveedor1['TOTAL_ACTIVOS_2021'] * 100
        rentabilidad1 = datos_proveedor1['GANANCIA_PERDIDA_2021'] / datos_proveedor1['INGRESOS_OPERACIONALES_2021'] * 100
        solvencia1 = datos_proveedor1['TOTAL_PATRIMONIO_2021'] / datos_proveedor1['TOTAL_PASIVOS_2021'] * 100
        razon_endeudamiento2 = datos_proveedor2['TOTAL_PASIVOS_2021'] / datos_proveedor2['TOTAL_ACTIVOS_2021'] * 100
        rentabilidad2 = datos_proveedor2['GANANCIA_PERDIDA_2021'] / datos_proveedor2['INGRESOS_OPERACIONALES_2021'] * 100
        solvencia2 = datos_proveedor2['TOTAL_PATRIMONIO_2021'] / datos_proveedor2['TOTAL_PASIVOS_2021'] * 100

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
        mejor_cumplimiento = data_simulada.loc[(data_simulada['GANANCIA_PERDIDA_2021'] / data_simulada['INGRESOS_OPERACIONALES_2021']).idxmax()]
        menor_riesgo = data_simulada.loc[(data_simulada['TOTAL_PASIVOS_2021'] / data_simulada['TOTAL_ACTIVOS_2021']).idxmin()]
        mas_sostenible = data_simulada.loc[(data_simulada['TOTAL_PATRIMONIO_2021'] / data_simulada['TOTAL_PASIVOS_2021']).idxmax()]

        st.write(f"- Mejor cumplimiento: **{mejor_cumplimiento['RAZON_SOCIAL']}** con {mejor_cumplimiento['GANANCIA_PERDIDA_2021'] / mejor_cumplimiento['INGRESOS_OPERACIONALES_2021'] * 100:.2f}%")
        st.write(f"- Menor riesgo financiero: **{menor_riesgo['RAZON_SOCIAL']}** con {menor_riesgo['TOTAL_PASIVOS_2021'] / menor_riesgo['TOTAL_ACTIVOS_2021'] * 100:.2f}%")
        st.write(f"- Más sostenible: **{mas_sostenible['RAZON_SOCIAL']}** con {mas_sostenible['TOTAL_PATRIMONIO_2021'] / mas_sostenible['TOTAL_PASIVOS_2021'] * 100:.2f}%")

        st.write("\nConsideraciones:")
        st.write("- Evalúe la posibilidad de aumentar la colaboración con proveedores de alto cumplimiento.")
        st.write("- Considere diversificar para mitigar riesgos con proveedores de alto riesgo financiero.")
        st.write("- Explore oportunidades para mejorar la sostenibilidad en su cadena de suministro.")