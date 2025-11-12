CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TABLE aula (
    id_aula SERIAL PRIMARY KEY,
    capacidad INTEGER NOT NULL,
    estado VARCHAR(50) DEFAULT 'Disponible');

CREATE TABLE horario (
    id_horario SERIAL PRIMARY KEY,
    id_aula INTEGER NOT NULL,
    turno VARCHAR(50),
    FOREIGN KEY (id_aula) REFERENCES aula(id_aula) ON DELETE CASCADE);

CREATE TABLE materia (
    id_materia VARCHAR(10) PRIMARY KEY,
    nombre_materia VARCHAR(100) NOT NULL,
    area VARCHAR(50));

CREATE TABLE materia_aula (
    id_materia VARCHAR(10) NOT NULL,
    id_aula INTEGER NOT NULL,
    PRIMARY KEY (id_materia, id_aula),
    FOREIGN KEY (id_materia) REFERENCES materia(id_materia) ON DELETE CASCADE,
    FOREIGN KEY (id_aula) REFERENCES aula(id_aula) ON DELETE CASCADE);

CREATE TABLE padre (
    id_padre SERIAL PRIMARY KEY,
    ci VARCHAR(20) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    ap_paterno VARCHAR(50),
    ap_materno VARCHAR(50),
    direccion VARCHAR(200),
    celular VARCHAR(20));

CREATE TABLE estudiante (
    id_estudiante SERIAL PRIMARY KEY,
    ci VARCHAR(20),
    nombres VARCHAR(100) NOT NULL,
    ap_paterno VARCHAR(50),
    ap_materno VARCHAR(50),
    rude VARCHAR(20) UNIQUE NOT NULL,
    grado VARCHAR(50) NOT NULL,
    id_padre INTEGER,
    FOREIGN KEY (id_padre) REFERENCES padre(id_padre) ON DELETE SET NULL);

CREATE TABLE estudiante_materia (
    id_estudiante INTEGER NOT NULL,
    id_materia VARCHAR(10) NOT NULL,
    PRIMARY KEY (id_estudiante, id_materia),
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materia(id_materia) ON DELETE CASCADE);

CREATE TABLE docente (
    ci VARCHAR(20) PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    ap_paterno VARCHAR(50),
    ap_materno VARCHAR(50),
    telefono_docente VARCHAR(20),
    fecha_ingreso DATE,
    sueldo DECIMAL(10, 2),
    id_materia VARCHAR(10),
    FOREIGN KEY (id_materia) REFERENCES materia(id_materia) ON DELETE SET NULL);