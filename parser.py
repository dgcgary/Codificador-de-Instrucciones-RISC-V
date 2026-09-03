import re

from instruction_set import SOPORTADAS


def parse_register(reg_str: str) -> int:
    """Extrae el número entero de un registro (ej. 'x5' -> 5)"""
    reg_str = reg_str.strip()

    # Verifica que el registro tenga exactamente el formato x seguido
    # de uno o más dígitos.
    match = re.fullmatch(r"x(\d+)", reg_str)
    if not match:
        raise ValueError(
            f"Registro inválido: {reg_str}. "
            "Debe utilizarse un registro entre x0 y x31."
        )

    register_number = int(match.group(1))

    # RV32I únicamente tiene los registros x0 hasta x31.
    if register_number < 0 or register_number > 31:
        raise ValueError(
            f"Registro inválido: {reg_str}. "
            "Los registros permitidos son x0 hasta x31."
        )

    return register_number


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


def parse_memory_operand(operand: str):
    # Busca un número opcionalmente negativo, seguido de "(x" y otro número ")".
    match = re.fullmatch(r"([+-]?\d+)\s*\(\s*x(\d+)\s*\)", operand)
    if not match:
        raise ValueError(f"Formato offset(rs1) inválido: {operand}")

    immediate = int(match.group(1))
    rs1 = parse_register("x" + match.group(2))
    return immediate, rs1
