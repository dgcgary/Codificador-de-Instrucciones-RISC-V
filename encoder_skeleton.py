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
import re

SOPORTADAS = ["add", "sub", "and", "or", "addi", "andi",
              "lw", "lb", "sw", "sb", "beq", "bne"]

# =====================================================================
# ESTRUCTURAS DE DATOS Y FUNCIONES DE PARSEO BÁSICO
# =====================================================================

INSTRUCTION_SET = {
    # Formato R
    "add":  {"formato": "R", "opcode": 0b0110011, "funct3": 0b000, "funct7": 0b0000000},
    "sub":  {"formato": "R", "opcode": 0b0110011, "funct3": 0b000, "funct7": 0b0100000},
    "and":  {"formato": "R", "opcode": 0b0110011, "funct3": 0b111, "funct7": 0b0000000},
    "or":   {"formato": "R", "opcode": 0b0110011, "funct3": 0b110, "funct7": 0b0000000},
    
    # Formato I Aritmético
    "addi": {"formato": "I", "opcode": 0b0010011, "funct3": 0b000},
    "andi": {"formato": "I", "opcode": 0b0010011, "funct3": 0b111},
    
    # Formato I Carga
    "lw":   {"formato": "I", "opcode": 0b0000011, "funct3": 0b010},
    "lb":   {"formato": "I", "opcode": 0b0000011, "funct3": 0b000},
    
    # Formato S
    "sw":   {"formato": "S", "opcode": 0b0100011, "funct3": 0b010},
    "sb":   {"formato": "S", "opcode": 0b0100011, "funct3": 0b000},
    
    # Formato B
    "beq":  {"formato": "B", "opcode": 0b1100011, "funct3": 0b000},
    "bne":  {"formato": "B", "opcode": 0b1100011, "funct3": 0b001},
}

def parse_register(reg_str: str) -> int:
    """Extrae el número entero de un registro (ej. 'x5' -> 5)"""
    reg_str = reg_str.strip()
    if reg_str.startswith("x"):
        return int(reg_str[1:])
    raise ValueError(f"Registro inválido: {reg_str}")

def parse_instruction(instruction: str):
    """Divide el texto ingresado en (mnemónico, resto_de_operandos)"""
    instruction = instruction.strip().lower()
    parts = instruction.split(None, 1)
    
    if len(parts) < 1:
        raise ValueError("Instrucción vacía")
    
    mnemonic = parts[0]
    operands_str = parts[1] if len(parts) > 1 else ""
    
    if mnemonic not in SOPORTADAS:
        raise ValueError(f"Instrucción no soportada: {mnemonic}")
    
    return mnemonic, operands_str

def encode_R(mnemonic: str, operands_str: str) -> int:
    spec = INSTRUCTION_SET[mnemonic]
    
    # Divide "x5, x6, x7" en una lista ["x5", "x6", "x7"]
    operands = [x.strip() for x in operands_str.split(",")]
    if len(operands) != 3:
        raise ValueError(f"Formato R requiere 3 operandos, obtuve: {operands_str}")
    
    rd = parse_register(operands[0])
    rs1 = parse_register(operands[1])
    rs2 = parse_register(operands[2])
    
    opcode = spec["opcode"]
    funct3 = spec["funct3"]
    funct7 = spec["funct7"]
    
    # Formato R: funct7[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    # Se desplaza cada valor a su posición de bits correspondiente y se unen con un OR (|)
    word = (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    return word

def encode_I(mnemonic: str, operands_str: str) -> int:
    spec = INSTRUCTION_SET[mnemonic]
    
    if mnemonic in ["lw", "lb"]:
        # Para cargas (lw, lb), el formato es: rd, offset(rs1)
        operands = [x.strip() for x in operands_str.split(",")]
        if len(operands) != 2:
            raise ValueError(f"Formato I carga requiere 2 operandos, obtuve: {operands_str}")
        
        rd = parse_register(operands[0])
        
        # Busca un número opcionalmente negativo, seguido de "(x" y otro número ")
        match = re.match(r"([+-]?\d+)\s*\(\s*x(\d+)\s*\)", operands[1])
        if not match:
            raise ValueError(f"Formato offset(rs1) inválido: {operands[1]}")
        
        imm = int(match.group(1))
        rs1 = int(match.group(2))
    else:
        # Para aritméticas (addi, andi), el formato es: rd, rs1, imm
        operands = [x.strip() for x in operands_str.split(",")]
        if len(operands) != 3:
            raise ValueError(f"Formato I aritmético requiere 3 operandos, obtuve: {operands_str}")
        
        rd = parse_register(operands[0])
        rs1 = parse_register(operands[1])
        imm = int(operands[2])
    
    # El inmediato en Formato I es de 12 bits. 
    # La máscara 0xFFF (4095 en decimal) fuerza la extensión de signo a nivel de 12 bits en Python.
    imm = imm & 0xFFF
    
    opcode = spec["opcode"]
    funct3 = spec["funct3"]
    
    # Formato I: imm[31:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    word = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    return word

def encode_S(mnemonic: str, operands_str: str) -> int:
    spec = INSTRUCTION_SET[mnemonic]
    
    # Para almacenamiento (sw, sb), el formato es: rs2, offset(rs1)
    operands = [x.strip() for x in operands_str.split(",")]
    if len(operands) != 2:
        raise ValueError(f"Formato S requiere 2 operandos, obtuve: {operands_str}")
    
    rs2 = parse_register(operands[0])
    
    match = re.match(r"([+-]?\d+)\s*\(\s*x(\d+)\s*\)", operands[1])
    if not match:
        raise ValueError(f"Formato offset(rs1) inválido: {operands[1]}")
    
    imm = int(match.group(1))
    rs1 = int(match.group(2))
    
    # Máscara de 12 bits para procesar negativos correctamente
    imm = imm & 0xFFF
    
    # El Formato S parte el inmediato en dos pedazos.
    # imm_high se lleva los 7 bits más significativos (bits 11 a 5).
    # imm_low se lleva los 5 bits menos significativos (bits 4 a 0).
    imm_high = (imm >> 5) & 0x7F  # 0x7F = 1111111 en binario
    imm_low = imm & 0x1F          # 0x1F = 11111 en binario
    
    opcode = spec["opcode"]
    funct3 = spec["funct3"]
    
    # Formato S: imm_high[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm_low[11:7] | opcode[6:0]
    word = (imm_high << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_low << 7) | opcode
    return word

def encode_B(mnemonic: str, operands_str: str) -> int:
    spec = INSTRUCTION_SET[mnemonic]
    
    # Para saltos condicionales (beq, bne), el formato es: rs1, rs2, imm
    operands = [x.strip() for x in operands_str.split(",")]
    if len(operands) != 3:
        raise ValueError(f"Formato B requiere 3 operandos, obtuve: {operands_str}")
    
    rs1 = parse_register(operands[0])
    rs2 = parse_register(operands[1])
    imm = int(operands[2])
    
    # Los saltos en RISC-V usan desplazamientos en múltiplos de 2 (el bit 0 siempre es 0).
    # Se procesa como un inmediato de 13 bits (máscara 0x1FFF).
    imm = imm & 0x1FFF
    
    # imm[12] va al bit 31
    # imm[10:5] van a los bits 30 al 25
    # imm[4:1] van a los bits 11 al 8
    # imm[11] va al bit 7
    imm_bit_12 = (imm >> 12) & 0x1
    imm_bits_10_5 = (imm >> 5) & 0x3F
    imm_bits_4_1 = (imm >> 1) & 0x0F
    imm_bit_11 = (imm >> 11) & 0x1
    
    opcode = spec["opcode"]
    funct3 = spec["funct3"]
    
    # Formato B ensamblado
    word = (imm_bit_12 << 31) | (imm_bits_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | \
           (funct3 << 12) | (imm_bits_4_1 << 8) | (imm_bit_11 << 7) | opcode
    return word

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
        return 0


def explain_instruction(instruction: str, word: int) -> str:
    """
    Debe retornar un texto (para imprimirse en pantalla) que muestre, de
    forma visual, los 32 bits de 'word' divididos en los campos del
    formato correspondiente (R, I, S o B) — indicando el rango de bits y
    el valor de cada campo — junto con una breve explicación de cada uno.
    El formato visual (colores, tabla, arte ASCII, etc.) queda a su
    criterio, siempre que sea claro.
    """
    return "Explicación pendiente de implementar."


def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} "<instruccion>"', file=sys.stderr)
        print(f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"', file=sys.stderr)
        sys.exit(2)

    instruction = sys.argv[1]
    word = encode_instruction(instruction) & 0xFFFFFFFF

    print(explain_instruction(instruction, word))

    # No modificar el formato de la siguiente línea: la especificación la
    # requiere, literal, para permitir la validación automática.
    print(f"HEX: 0x{word:08x}")


if __name__ == "__main__":
    main()