# Proyecto Individual
# Arquitectura de Computadores I
# David Garcia Cruz - 2024115575

## Preparación del entorno

El proyecto requiere un entorno Linux o WSL con Python 3, Bash y la
toolchain de RISC-V instalada.

La toolchain utilizada es riscv64-unknown-elf-gcc versión 14.2.0.
También se utiliza riscv64-unknown-elf-objdump para consultar las
codificaciones generadas por el ensamblador.

En Ubuntu/WSL se instalaron los componentes con:

```bash
sudo apt update
sudo apt install -y gcc-riscv64-unknown-elf python3 python3-pip git
```

No se requieren dependencias externas de Python ni un entorno virtual.

## Punto de entrada

El punto de entrada del proyecto es el script run.sh, ubicado en la raíz.
Debe recibir una única instrucción como argumento:

```bash
./run.sh "add x5, x6, x7"
```

La salida incluye una explicación de los campos de la instrucción y una
línea procesable con el formato:

```text
HEX: 0xXXXXXXXX
```
En caso de no funcionar el comando por permisos del sistema se debe ejecutar:
```bash
chmod +x run.sh
```  

## Validación

La validación contra la toolchain oficial se ejecuta con:

```bash
python3 validate_toolchain.py
```

El script compara 36 casos entre el codificador del proyecto y
riscv64-unknown-elf-objdump.
