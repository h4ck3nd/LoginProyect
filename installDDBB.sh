#!/bin/bash

# Verificar si el script se ejecuta como root
if [[ $(id -u) -ne 0 ]]; then
    echo "❌ Este script debe ejecutarse como root o con sudo."
    exit 1
fi

echo "✅ Iniciando instalación y configuración de PostgreSQL..."

# Actualizar repositorios e instalar PostgreSQL
apt update && apt install -y postgresql postgresql-contrib

# Habilitar y arrancar PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Configurar PostgreSQL
echo "🔑 Configurando usuario y base de datos en PostgreSQL..."
sudo -u postgres psql <<EOF
CREATE DATABASE login;
GRANT ALL PRIVILEGES ON DATABASE login TO postgres;
ALTER ROLE postgres SET client_encoding TO 'UTF8';
ALTER USER postgres WITH PASSWORD '1234';
EOF

echo "✅ Base de datos y usuario configurados."

# Instalar psycopg2 para Python
echo "🐍 Instalando librería psycopg2 para conectar con Python..."
pip install psycopg2

# Crear la tabla dentro de la base de datos
echo "📦 Creando la estructura de la base de datos..."
sudo -u postgres psql -d login <<EOF
CREATE TABLE IF NOT EXISTS users (
    id serial PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    fechaNacimiento DATE NOT NULL,
    estado BOOLEAN DEFAULT true,
    fechaRegistro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rol VARCHAR(5) DEFAULT 'user',
    ultimo_login TIMESTAMP
);
ALTER TABLE users ADD COLUMN username VARCHAR(50) UNIQUE NOT NULL;
EOF

echo "✅ Base de datos configurada correctamente."

# Mensaje final
echo "🎉 Instalación y configuración completadas."
echo "Para acceder a PostgreSQL: sudo -u postgres psql -d login"
