from instruction_set import INSTRUCTION_SET
from parser import parse_register


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
