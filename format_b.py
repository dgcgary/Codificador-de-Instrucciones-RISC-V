from instruction_set import INSTRUCTION_SET
from parser import parse_register


def encode_B(mnemonic: str, operands_str: str) -> int:
    spec = INSTRUCTION_SET[mnemonic]
    
    # Para saltos condicionales (beq, bne), el formato es: rs1, rs2, imm
    operands = [x.strip() for x in operands_str.split(",")]
    if len(operands) != 3:
        raise ValueError(f"Formato B requiere 3 operandos, obtuve: {operands_str}")
    
    rs1 = parse_register(operands[0])
    rs2 = parse_register(operands[1])
    immediate = int(operands[2])
    
    # Los saltos en RISC-V usan desplazamientos en múltiplos de 2 (el bit 0 siempre es 0).
    # Se procesa como un inmediato de 13 bits (máscara 0x1FFF).

    # Un inmediato de branch de 13 bits con signo puede representar
    # valores desde -4096 hasta 4094.
    if immediate < -4096 or immediate > 4094:
        raise ValueError(
            f"Offset fuera de rango: {immediate}. "
            "El rango permitido es -4096 hasta 4094."
        )

    # El bit menos significativo debe ser cero porque los offsets
    # de branch siempre son pares.
    if immediate % 2 != 0:
        raise ValueError(
            f"Offset inválido: {immediate}. "
            "Los offsets de branch deben ser pares."
        )

    immediate = immediate & 0x1FFF
    
    # imm[12] va al bit 31
    # imm[10:5] van a los bits 30 al 25
    # imm[4:1] van a los bits 11 al 8
    # imm[11] va al bit 7
    imm_bit_12 = (immediate >> 12) & 0x1
    imm_bits_10_5 = (immediate >> 5) & 0x3F
    imm_bits_4_1 = (immediate >> 1) & 0x0F
    imm_bit_11 = (immediate >> 11) & 0x1
    
    opcode = spec["opcode"]
    funct3 = spec["funct3"]
    
    # Formato B ensamblado
    word = (imm_bit_12 << 31) | (imm_bits_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | \
           (funct3 << 12) | (imm_bits_4_1 << 8) | (imm_bit_11 << 7) | opcode
    return word
