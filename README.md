🛡️ Auditoría de Licencias 365
Optimización de costos y auditoría automatizada para Microsoft 365.

Esta herramienta de código abierto ayuda a los departamentos de TI a eliminar los "costos zombis": licencias de software activas asignadas a usuarios que ya han sido bloqueados o dados de baja.

¿Qué hace? Procesa reportes .csv de Microsoft 365/Azure AD y cruza automáticamente el estado de las credenciales con las licencias asignadas. Identifica en segundos cuánto dinero se está desperdiciando en cuentas inactivas.

Características Principales:

Privacidad Total: Ejecución 100% local o en servidor propio (Docker); los datos nunca salen de tu infraestructura.

Análisis Rápido: Interfaz "Drag & Drop" para reportes CSV manuales.

Dashboard Interactivo: Visualiza el desperdicio por tipo de licencia (E3, Business Standard, Power BI, etc.) y genera listas detalladas para la remediación.

Tech Stack: Python 3.9 • Streamlit • Pandas • Docker


📂 Estructura del Proyecto
Tu repositorio en GitHub debería verse así:

Plaintext
auditoria-365/
├── app.py               # El código principal (tu versión final)
├── Dockerfile           # Instrucciones para crear el contenedor
├── docker-compose.yml   # Para levantar el proyecto fácil
├── requirements.txt     # Librerías necesarias
├── README.md            # Documentación del proyecto
└── data/                # Carpeta para guardar los CSV
1. El Código Principal (app.py)
Este es exactamente el código que me pasaste.

Python
import streamlit as st
import pandas as pd
import os
import glob

# Configuración: Layout "wide" para aprovechar el ancho, pero diseño compacto
st.set_page_config(page_title="Auditoría de Licencias", layout="wide")

# --- Encabezado y Carga de Archivos ---
col1, col2 = st.columns([2, 1.5])
with col1:
    st.title("🔒 Reporte de Usuarios Bloqueados")

with col2:
    uploaded_file = st.file_uploader(
        "📂 Cargar o actualizar reporte",
        type=["csv"],
        help="Sube un archivo .csv para analizar o actualizar el reporte."
    )
st.divider()

# --- LÓGICA DE CARGA DE DATOS ---

df = None
source_message = ""

if uploaded_file is not None:
    # Si se sube un archivo, se guarda en la carpeta 'data' y se procesa
    try:
        DATA_FOLDER = './data'
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        
        save_path = os.path.join(DATA_FOLDER, uploaded_file.name)
        
        # Guardar el contenido del archivo subido en el servidor
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Leer el dataframe desde el archivo recién guardado
        df = pd.read_csv(save_path)
        source_message = f"Se guardó y ahora se muestran los datos de: **{uploaded_file.name}**"
        st.success(f"Archivo '{uploaded_file.name}' guardado en el servidor.")

    except Exception as e:
        st.error(f"Error al guardar o procesar el archivo: {e}")
else:
    # Si no, busca el último archivo en la carpeta 'data'
    DATA_FOLDER = './data'
    list_of_files = glob.glob(os.path.join(DATA_FOLDER, '*.csv'))

    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        try:
            df = pd.read_csv(latest_file)
            source_message = f"Mostrando datos del archivo local: **{os.path.basename(latest_file)}**"
        except Exception as e:
            st.error(f"Error al leer el archivo local: {e}")

# --- INICIO DE LA APP PRINCIPAL ---
if df is not None:
    st.markdown(source_message) # Muestra de dónde vienen los datos
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
            
            # Initialize session state for filter
            if 'licencia_seleccionada' not in st.session_state:
                st.session_state.licencia_seleccionada = None

            # Custom table with buttons
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
            
            # Detectar si hay una licencia seleccionada en el estado de la sesión
            if st.session_state.licencia_seleccionada:
                licencia_seleccionada = st.session_state.licencia_seleccionada
                
                # Aplicar filtro
                df_filtrado = df_bloqueados[df_bloqueados['Licenses'].str.contains(licencia_seleccionada, regex=False)]
                mensaje_filtro = f"Filtro Activo: Usuarios con {licencia_seleccionada}"
                
                # Botón para borrar filtro (solo aparece si hay filtro)
                if st.button("❌ Quitar Filtro"):
                    st.session_state.licencia_seleccionada = None
                    st.rerun() # Esto recargará la página limpia

            # --- PARTE 3: INVENTARIO DETALLADO ---
            
            col_header, col_count = st.columns([8, 2])
            col_header.subheader("📋 Inventario Detallado")
            col_count.metric("Usuarios en lista", len(df_filtrado))
            
            st.info(mensaje_filtro)

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
else:
    st.info("Para comenzar, carga un reporte usando el panel de arriba o asegúrate de que haya un archivo .csv en la carpeta 'data' del servidor.")
2. Dependencias (requirements.txt)
Solo necesitamos lo básico para procesar datos y mostrarlos.

Plaintext
streamlit
pandas
3. Dockerfile
Para que cualquiera pueda construir la imagen sin configurar Python manualmente.

Dockerfile
# Imagen base ligera de Python
FROM python:3.9-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Crear carpeta de datos por si no existe
RUN mkdir -p data

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando de ejecución
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
4. Docker Compose (docker-compose.yml)
Este archivo hace que desplegarlo sea tan fácil como escribir un comando.

YAML
version: '3'
services:
  auditoria-365:
    build: .
    container_name: auditoria_licencias_manual
    ports:
      - "8501:8501"
    volumes:
      # Persistencia: los archivos subidos quedan guardados en la carpeta ./data
      - ./data:/app/data
    restart: unless-stopped
5. Documentación (README.md)
Copia esto en tu repositorio para explicar cómo se usa.

Markdown
# 🔒 Auditoría de Licencias 365 (CSV Analyzer)

Esta herramienta permite cargar reportes de usuarios de Microsoft 365 (en formato `.csv`) para identificar rápidamente licencias asignadas a usuarios que ya están bloqueados (desperdicio de licencias).

## ✨ Características

* **Carga Manual:** Interfaz "Drag & Drop" para subir reportes CSV.
* **Persistencia:** Los archivos subidos se guardan en el servidor para revisiones futuras.
* **Filtrado Inteligente:** Detecta automáticamente usuarios con `Block credential = True`.
* **Dashboard Interactivo:**
    * Resumen de licencias desperdiciadas por tipo.
    * Botones para filtrar la lista detallada.
    * Tabla de inventario detallado.

## 📋 Requisitos del CSV

Para que la herramienta funcione, el archivo CSV debe contener (al menos) estas columnas exactas exportadas de Microsoft 365 o Azure AD:

* `Block credential` (Debe contener valores True/False)
* `Licenses`
* `Display name`
* `User principal name`

## 🚀 Instalación y Despliegue

### Opción A: Usando Docker Compose (Recomendado)

1.  Clona este repositorio o descarga los archivos.
2.  Ejecuta el siguiente comando en la terminal:

```bash
docker-compose up -d --build
Accede a la aplicación en tu navegador: http://localhost:8501 (o la IP de tu servidor).

Opción B: Ejecución Manual (Python)
Crea un entorno virtual:

Bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
Instala las dependencias:

Bash
pip install -r requirements.txt
Ejecuta la aplicación:

Bash
streamlit run app.py
📂 Estructura de Archivos
app.py: Lógica principal de la aplicación.

data/: Carpeta donde se almacenan los reportes cargados.


---

### Comandos para implementarlo manualmente en tu servidor Linux

Si quieres subir esto ya mismo a tu servidor `/opt`, estos son los pasos "copiar y pegar":

```bash
# 1. Crear carpeta del proyecto
sudo mkdir -p /opt/docker/auditoria_manual
cd /opt/docker/auditoria_manual

# 2. Crear los archivos (Usa nano para pegar el contenido de arriba en cada uno)
sudo nano app.py              # <--- Pega el código Python
sudo nano requirements.txt    # <--- Pega streamlit y pandas
sudo nano Dockerfile          # <--- Pega el código Dockerfile
sudo nano docker-compose.yml  # <--- Pega el código YAML

# 3. Crear carpeta de datos
sudo mkdir data

# 4. Levantar el servicio
sudo docker-compose up -d --build