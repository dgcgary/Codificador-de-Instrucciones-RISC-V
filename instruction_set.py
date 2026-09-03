# =====================================================================
# TABLA DE INSTRUCCIONES SOPORTADAS
# =====================================================================

SOPORTADAS = ["add", "sub", "and", "or", "addi", "andi",
              "lw", "lb", "sw", "sb", "beq", "bne"]

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
