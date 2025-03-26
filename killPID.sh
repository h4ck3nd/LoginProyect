programa=$1

nombre=$(ps -p $programa -o comm=)
kill $programa

echo "proceso '$nombre' matado con exito!"