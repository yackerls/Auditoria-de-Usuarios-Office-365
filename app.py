import streamlit as st
import pandas as pd

# Configuración: Layout "wide"
st.set_page_config(page_title="Auditoría de Licencias", layout="wide")

# --- Encabezado y Carga de Archivos ---
col1, col2 = st.columns([2, 1.5])
with col1:
    st.title("🔒 Reporte de Usuarios Bloqueados")
    st.caption("Modo Privacidad: Los datos se procesan en memoria y no se guardan.")

with col2:
    uploaded_file = st.file_uploader(
        "📂 Cargar reporte (.csv)",
        type=["csv"],
        help="Sube un archivo para analizarlo al instante. No se guardará copia en el servidor."
    )
st.divider()

# --- LÓGICA DE CARGA (SOLO MEMORIA) ---

df = None
source_message = ""

if uploaded_file is not None:
    try:
        # LEER DIRECTAMENTE DESDE LA SUBIDA (Sin guardar en disco)
        df = pd.read_csv(uploaded_file)
        source_message = f"✅ Analizando archivo temporal: **{uploaded_file.name}**"
        
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("👈 Sube un archivo CSV en el panel de arriba para ver el reporte.")

# --- INICIO DE LA APP PRINCIPAL ---
if df is not None:
    st.success(source_message)
    try:
        if 'Block credential' in df.columns and 'Licenses' in df.columns:
            
            # --- PREPARAR DATOS ---
            df_bloqueados = df[df['Block credential'] == True].copy()
            df_bloqueados['Licenses'] = df_bloqueados['Licenses'].fillna('')

            licencias_a_buscar = [
                "Exchange Online (plan 1)",
                "Microsoft 365 Empresa Básico",
                "Microsoft 365 Empresa Premium",
                "Microsoft 365 Empresa Estándar",
                "Power BI Pro",
                "Power BI Premium"
            ]
            
            # --- PARTE 1: TABLA RESUMEN COMPACTA ---
            resultados = []
            for licencia in licencias_a_buscar:
                conteo = df_bloqueados['Licenses'].str.contains(licencia, regex=False).sum()
                resultados.append({
                    "Licencia": licencia,
                    "Usuarios": conteo,
                })
            
            df_resumen = pd.DataFrame(resultados)

            st.markdown("### 📉 Resumen de Desperdicio")
            st.caption("Haz clic en 'Ver' para filtrar la lista de abajo.")
            
            # Estado de la sesión para filtros
            if 'licencia_seleccionada' not in st.session_state:
                st.session_state.licencia_seleccionada = None

            # Tabla personalizada con botones
            header_cols = st.columns([3, 1, 1])
            header_cols[0].markdown("**Tipo de Licencia**")
            header_cols[1].markdown("**Cantidad Bloqueada**")
            header_cols[2].markdown("**Acción**")
            st.markdown("<hr style='margin:0.5rem 0; border-top: 1px solid rgba(0, 0, 0, 0.1);'>", unsafe_allow_html=True)

            for index, row in df_resumen.iterrows():
                row_cols = st.columns([3, 1, 1])
                row_cols[0].write(row["Licencia"])
                row_cols[1].write(f"{row['Usuarios']} 👤")
                if row_cols[2].button("🔍 Ver", key=f"view_button_{index}"):
                    st.session_state.licencia_seleccionada = row["Licencia"]
                    st.rerun()
                if index < len(df_resumen) - 1:
                    st.markdown("<hr style='margin:0.5rem 0; border-top: 1px solid rgba(0, 0, 0, 0.1);'>", unsafe_allow_html=True)
            
            st.divider()

            # --- PARTE 2: LÓGICA DE FILTRADO ---
            
            df_filtrado = df_bloqueados
            mensaje_filtro = "Mostrando: Todos los usuarios bloqueados"
            
            if st.session_state.licencia_seleccionada:
                licencia_seleccionada = st.session_state.licencia_seleccionada
                
                # Aplicar filtro
                df_filtrado = df_bloqueados[df_bloqueados['Licenses'].str.contains(licencia_seleccionada, regex=False)]
                mensaje_filtro = f"Filtro Activo: Usuarios con {licencia_seleccionada}"
                
                if st.button("❌ Quitar Filtro"):
                    st.session_state.licencia_seleccionada = None
                    st.rerun()

            # --- PARTE 3: INVENTARIO DETALLADO ---
            
            col_header, col_count = st.columns([8, 2])
            col_header.subheader("📋 Inventario Detallado")
            
            st.info(mensaje_filtro)

            search_query = st.text_input("🔍 Buscar en la tabla:", placeholder="Escribe un nombre, correo, puesto, etc.")

            # Mapeo de columnas
            cols_map = {
                'Display name': 'Nombre',
                'User principal name': 'Correo',
                'Title': 'Puesto',
                'Department': 'Departamento',
                'Office': 'Región',
                'Licenses': 'Licencia',
                'When created': 'Fecha de Creación',
                'Last password change time stamp': 'Último Cambio de Pass'
            }
            
            cols_existentes = [c for c in cols_map.keys() if c in df_filtrado.columns]
            
            if cols_existentes:
                df_final = df_filtrado[cols_existentes].rename(columns=cols_map)

                # Lógica de búsqueda
                if search_query:
                    # Crear una máscara booleana con False por defecto
                    mask = pd.Series([False] * len(df_final))
                    # Iterar sobre las columnas de df_final para buscar el texto
                    for col in df_final.columns:
                        mask = mask | df_final[col].astype(str).str.contains(search_query, case=False, na=False)
                    df_final = df_final[mask]

                col_count.metric("Usuarios en lista", len(df_final))
                
                st.dataframe(
                    df_final,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No se encontraron columnas de detalle.")

        else:
            st.error("El archivo CSV debe contener las columnas 'Block credential' y 'Licenses'.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los datos: {e}")