# 🛡️ Auditoría de Licencias 365

### Optimización de costos y auditoría automatizada para Microsoft 365

Esta herramienta de código abierto ayuda a los departamentos de TI a eliminar los **"costos zombis"**: licencias de software activas asignadas a usuarios que ya han sido bloqueados o dados de baja.

---

## 📌 ¿Qué hace este proyecto?

Procesa reportes `.csv` exportados de Microsoft 365 o Azure AD y cruza automáticamente el estado de las credenciales con las licencias asignadas.

**El resultado:** Identifica en segundos cuánto dinero se está desperdiciando en cuentas inactivas.

---

## ✨ Características Principales
* 🔒 **Privacidad Total:** Ejecución 100% local o en servidor propio (Docker); los datos sensibles nunca salen de tu infraestructura.
* 📂 **Análisis Rápido:** Interfaz "Drag & Drop" para cargar reportes CSV manualmente.
* 📊 **Dashboard Interactivo:** Visualiza el desperdicio por tipo de licencia (E3, Business Standard, Power BI, etc.).
* 📋 **Listas Detalladas:** Genera tablas filtrables para facilitar la remediación y limpieza de usuarios.

---

## 🛠️ Tecnologías Usadas

* ![Python](https://img.shields.io/badge/Python-3.9-blue?style=flat&logo=python)
* ![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red?style=flat&logo=streamlit)
* ![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=flat&logo=pandas)
* ![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=flat&logo=docker)

---

## 🚀 Instalación y Uso

### Opción A: Usando Docker (Recomendado)

1.  **Clona el repositorio:**
    ```bash
    sudo git clone https://github.com/yackerls/Auditoria-de-Usuarios-Office-365.git
    cd Auditoria-de-Usuarios-Office-365
    ```

2.  **Levanta el contenedor:**
    *(Nota: Usamos el comando moderno `docker compose` con espacio)*
    ```bash
    sudo docker compose up -d --build
    ```
    *Si tu versión de Docker es antigua y falla el comando anterior, intenta con `sudo docker-compose up -d --build`.*

3.  **Accede a la herramienta:**
    Abre tu navegador y ve a `http://localhost:8501`.

### Opción B: Ejecución Manual (Python)

1.  Crea un entorno virtual e instala las dependencias:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  Ejecuta la aplicación:
    ```bash
    streamlit run app.py
    ```

---

## 📋 Requisitos del CSV

Para que el análisis funcione, tu archivo `.csv` debe contener al menos estas columnas (tal como se exportan de Azure AD/M365):

| Columna Requerida | Descripción |
| :--- | :--- |
| `Block credential` | Estado del usuario (`True` = Bloqueado). |
| `Licenses` | Lista de licencias asignadas. |
| `Display name` | Nombre del usuario. |
| `User principal name` | Correo electrónico. |

---

## 📂 Estructura del Proyecto

```text
auditoria-365/
├── app.py               # Lógica principal de la aplicación
├── Dockerfile           # Configuración de la imagen Docker
├── docker-compose.yml   # Orquestación del contenedor
├── requirements.txt     # Librerías de Python necesarias
├── README.md            # Documentación
└── data/                # Carpeta local para almacenar reportes


```

---

## 📸 Captura de Pantalla

Así se ve el dashboard interactivo:

![Dashboard de Auditoría](screenshot.png)

---