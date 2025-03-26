#!/bin/bash

# Verificar si se pasaron los tres argumentos necesarios
if [ "$#" -ne 3 ]; then
    echo "Uso: $0 <ruta_origen> <ruta_destino> <frecuencia_minutos>"
    exit 1
fi

# Asignar argumentos a variables
RUTA_ORIGEN=$1
RUTA_DESTINO=$2
FRECUENCIA=$3

# Crear el comando de copia
COMANDO="cp -r \"$RUTA_ORIGEN\" \"$RUTA_DESTINO\""

# Agregar tarea al crontab del usuario
(crontab -l 2>/dev/null; echo "*/$FRECUENCIA * * * * $COMANDO") | crontab -

echo "Copia de seguridad programada cada $FRECUENCIA minutos."