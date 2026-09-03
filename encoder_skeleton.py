#!/usr/bin/env python3
"""
Esqueleto del Codificador Educativo de Instrucciones RISC-V.
CE4301 Arquitectura de Computadores I — Proyecto Individual — 2026-II

Este esqueleto ya implementa el contrato de línea de comandos y de salida
requerido por la especificación. Usted debe completar las dos funciones
marcadas con TODO; puede modificar el resto del archivo si lo necesita,
siempre que se preserve el contrato de invocación y la línea "HEX: 0x...".

No es obligatorio usar este esqueleto ni Python: puede implementar su
propia herramienta desde cero, en el lenguaje que prefiera, siempre que
respete el mismo contrato (ver especificación, sección "Modo de operación").
"""
import sys

from explanation import explain_instruction
from format_b import encode_B
from format_i import encode_I
from format_r import encode_R
from format_s import encode_S
from instruction_set import INSTRUCTION_SET
from parser import parse_instruction


def encode_instruction(instruction: str) -> int:
    """
    Recibe una instrucción como texto, p. ej. "add x5, x6, x7", y debe
    retornar su codificación de 32 bits como entero (0 <= valor < 2**32).

    Debe soportar únicamente las instrucciones en SOPORTADAS. Los valores
    de opcode/funct3/funct7 de cada una NO se proveen aquí: deben
    investigarse en el manual oficial de la ISA RISC-V (ver referencia en
    la especificación) y documentarse en el README.
    """
    mnemonic, operands_str = parse_instruction(instruction)
    spec = INSTRUCTION_SET[mnemonic]
    formato = spec["formato"]
    
    if formato == "R":
        return encode_R(mnemonic, operands_str)
    elif formato == "I":
        return encode_I(mnemonic, operands_str)
    elif formato == "S":
        return encode_S(mnemonic, operands_str)
    elif formato == "B":
        return encode_B(mnemonic, operands_str)
    else:
        raise ValueError(f"Formato desconocido: {formato}")


def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} "<instruccion>"', file=sys.stderr)
        print(f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"', file=sys.stderr)
        sys.exit(2)

    instruction = sys.argv[1]

    try:
        word = encode_instruction(instruction) & 0xFFFFFFFF
    except ValueError as error:
        # Los errores de validación se muestran sin generar una codificación.
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    print(explain_instruction(instruction, word))

    # No modificar el formato de la siguiente línea: la especificación la
    # requiere, literal, para permitir la validación automática.
    print(f"HEX: 0x{word:08x}")


if __name__ == "__main__":
    main()
