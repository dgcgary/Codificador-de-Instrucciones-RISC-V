from instruction_set import INSTRUCTION_SET
from parser import parse_memory_operand, parse_register


def encode_S(mnemonic: str, operands_str: str) -> int:
    spec = INSTRUCTION_SET[mnemonic]
    
    # Para almacenamiento (sw, sb), el formato es: rs2, offset(rs1)
    operands = [x.strip() for x in operands_str.split(",")]
    if len(operands) != 2:
        raise ValueError(f"Formato S requiere 2 operandos, obtuve: {operands_str}")
    
    rs2 = parse_register(operands[0])
    immediate, rs1 = parse_memory_operand(operands[1])

    # Un inmediato de 12 bits con signo puede representar valores
    # desde -2048 hasta 2047.
    if immediate < -2048 or immediate > 2047:
        raise ValueError(
            f"Inmediato fuera de rango: {immediate}. "
            "El rango permitido es -2048 hasta 2047."
        )
    
    # Máscara de 12 bits para procesar negativos correctamente
    immediate = immediate & 0xFFF
    
    # El Formato S parte el inmediato en dos pedazos.
    # imm_high se lleva los 7 bits más significativos (bits 11 a 5).
    # imm_low se lleva los 5 bits menos significativos (bits 4 a 0).
    imm_high = (immediate >> 5) & 0x7F
    imm_low = immediate & 0x1F
    
    opcode = spec["opcode"]
    funct3 = spec["funct3"]
    
    # Formato S: imm_high[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm_low[11:7] | opcode[6:0]
    word = (imm_high << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_low << 7) | opcode
    return word
