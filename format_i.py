from instruction_set import INSTRUCTION_SET
from parser import parse_memory_operand, parse_register


def encode_I(mnemonic: str, operands_str: str) -> int:
    spec = INSTRUCTION_SET[mnemonic]
    
    if mnemonic in ["lw", "lb"]:
        # Para cargas (lw, lb), el formato es: rd, offset(rs1)
        operands = [x.strip() for x in operands_str.split(",")]
        if len(operands) != 2:
            raise ValueError(f"Formato I carga requiere 2 operandos, obtuve: {operands_str}")
        
        rd = parse_register(operands[0])
        immediate, rs1 = parse_memory_operand(operands[1])
    else:
        # Para aritméticas (addi, andi), el formato es: rd, rs1, imm
        operands = [x.strip() for x in operands_str.split(",")]
        if len(operands) != 3:
            raise ValueError(f"Formato I aritmético requiere 3 operandos, obtuve: {operands_str}")
        
        rd = parse_register(operands[0])
        rs1 = parse_register(operands[1])
        immediate = int(operands[2])

    # Un inmediato de 12 bits con signo puede representar valores
    # desde -2048 hasta 2047.
    if immediate < -2048 or immediate > 2047:
        raise ValueError(
            f"Inmediato fuera de rango: {immediate}. "
            "El rango permitido es -2048 hasta 2047."
        )
    
    # El inmediato en Formato I es de 12 bits. 
    # La máscara 0xFFF (4095 en decimal) fuerza la extensión de signo a nivel de 12 bits en Python.
    immediate = immediate & 0xFFF
    
    opcode = spec["opcode"]
    funct3 = spec["funct3"]
    
    # Formato I: imm[31:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    word = (immediate << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    return word
