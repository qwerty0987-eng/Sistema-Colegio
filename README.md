## Sistema de Registro Escolar (Python + PostgreSQL)

Este proyecto es una aplicación de escritorio hecha con **Python**, **Tkinter**, y **ttkbootstrap** para la gestión de registros escolares: materias, docentes, padres y estudiantes.

---

## Características principales
- CRUD completo (Agregar, Actualizar, Eliminar, Buscar)
- Interfaz moderna con `ttkbootstrap`
- Conexión directa a base de datos PostgreSQL
- Filtrado y búsqueda con `ILIKE` y `unaccent` (para búsquedas sin tildes)
- Paleta de colores oscura personalizable (`temas.py`)

---

## Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- **Python 3.10+**
- **PostgreSQL** (con una base de datos creada)
- Ingresar los datos necesarios en el archivo 'database.py'
- Librerías necesarias:

* pip install psycopg2-binary
* pip install ttkbootstrap
* pip install pillow
