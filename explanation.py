from instruction_set import INSTRUCTION_SET
from parser import parse_instruction


def get_binary_field(word: int, high_bit: int, low_bit: int) -> str:
    """
    Extrae un campo de la instrucción y lo devuelve en binario.

    Los bits se numeran desde el bit 31, que es el más significativo,
    hasta el bit 0, que es el menos significativo.
    """

    field_size = high_bit - low_bit + 1
    field_mask = (1 << field_size) - 1
    field_value = (word >> low_bit) & field_mask

    return format(field_value, f"0{field_size}b")


def signed_value(binary_value: str) -> int:
    """
    Interpreta una cadena binaria como un número con signo en complemento
    a dos.

    Si el primer bit es 1, el valor representa un número negativo.
    """

    value = int(binary_value, 2)
    bit_count = len(binary_value)

    if binary_value[0] == "1":
        value -= 1 << bit_count

    return value


def format_field(field_name: str, bit_range: str, binary_value: str,
                 explanation: str) -> str:
    """
    Construye una fila de la tabla ASCII de campos.

    Cada fila muestra el nombre del campo, su rango de bits, su valor
    binario y una explicación de su función.
    """

    # Se agregan espacios al final de la explicación para que el separador
    # derecho quede alineado con la tabla.
    return (
        f"| {field_name:<11} | {bit_range:<9} | "
        f"{binary_value:<12} | {explanation:<70} "
    )


def explain_instruction(instruction: str, word: int) -> str:
    """
    Muestra una representación ASCII de la instrucción.

    Primero identifica el formato. Después extrae cada campo de la palabra
    de 32 bits y presenta su valor binario, decimal y significado.
    """

    # Se obtiene el mnemónico y el texto de los operandos.
    mnemonic, operands_str = parse_instruction(instruction)
    instruction_format = INSTRUCTION_SET[mnemonic]["formato"]

    # Se preparan los campos que aparecerán en la tabla.
    fields = []
    explanations = []

    if instruction_format == "R":
        # Se extraen los campos del formato R.
        funct7 = get_binary_field(word, 31, 25)
        rs2 = get_binary_field(word, 24, 20)
        rs1 = get_binary_field(word, 19, 15)
        funct3 = get_binary_field(word, 14, 12)
        rd = get_binary_field(word, 11, 7)
        opcode = get_binary_field(word, 6, 0)

        fields = [
            ("funct7", "[31:25]", funct7),
            ("rs2", "[24:20]", rs2),
            ("rs1", "[19:15]", rs1),
            ("funct3", "[14:12]", funct3),
            ("rd", "[11:7]", rd),
            ("opcode", "[6:0]", opcode),
        ]

        explanations = [
            f"funct7 identifica la variante de {mnemonic}.",
            f"rs2 = {int(rs2, 2)} (x{int(rs2, 2)}), segundo registro fuente.",
            f"rs1 = {int(rs1, 2)} (x{int(rs1, 2)}), primer registro fuente.",
            "funct3 identifica la operación dentro del opcode.",
            f"rd = {int(rd, 2)} (x{int(rd, 2)}), registro destino.",
            "opcode identifica una instrucción aritmética de formato R.",
        ]

    elif instruction_format == "I":
        # Se extraen los campos comunes del formato I.
        immediate = get_binary_field(word, 31, 20)
        rs1 = get_binary_field(word, 19, 15)
        funct3 = get_binary_field(word, 14, 12)
        rd = get_binary_field(word, 11, 7)
        opcode = get_binary_field(word, 6, 0)

        fields = [
            ("imm[11:0]", "[31:20]", immediate),
            ("rs1", "[19:15]", rs1),
            ("funct3", "[14:12]", funct3),
            ("rd", "[11:7]", rd),
            ("opcode", "[6:0]", opcode),
        ]

        # Las instrucciones I utilizan inmediatos con signo.
        immediate_decimal = signed_value(immediate)

        explanations = [
            (
                f"imm[11:0] = {immediate_decimal}. "
                "Es el inmediato en complemento a dos."
            ),
            f"rs1 = {int(rs1, 2)} (x{int(rs1, 2)}), registro fuente o base.",
            "funct3 identifica la operación o el tamaño de la carga.",
            f"rd = {int(rd, 2)} (x{int(rd, 2)}), registro destino.",
            "opcode identifica una instrucción de formato I.",
        ]

    elif instruction_format == "S":
        # Se extraen las partes separadas del inmediato del formato S.
        immediate_high = get_binary_field(word, 31, 25)
        rs2 = get_binary_field(word, 24, 20)
        rs1 = get_binary_field(word, 19, 15)
        funct3 = get_binary_field(word, 14, 12)
        immediate_low = get_binary_field(word, 11, 7)
        opcode = get_binary_field(word, 6, 0)

        immediate = immediate_high + immediate_low
        immediate_decimal = signed_value(immediate)

        fields = [
            ("imm[11:5]", "[31:25]", immediate_high),
            ("rs2", "[24:20]", rs2),
            ("rs1", "[19:15]", rs1),
            ("funct3", "[14:12]", funct3),
            ("imm[4:0]", "[11:7]", immediate_low),
            ("opcode", "[6:0]", opcode),
        ]

        explanations = [
            (
                f"imm[11:5] es parte del offset. "
                f"El inmediato completo es {immediate_decimal}."
            ),
            f"rs2 = {int(rs2, 2)} (x{int(rs2, 2)}), registro que se almacena.",
            f"rs1 = {int(rs1, 2)} (x{int(rs1, 2)}), registro base de memoria.",
            "funct3 identifica el tamaño de la operación de almacenamiento.",
            "imm[4:0] completa el offset de 12 bits.",
            "opcode identifica una instrucción de formato S.",
        ]

    elif instruction_format == "B":
        # Se extraen las partes reorganizadas del inmediato del formato B.
        immediate_bit_12 = get_binary_field(word, 31, 31)
        immediate_bits_10_5 = get_binary_field(word, 30, 25)
        rs2 = get_binary_field(word, 24, 20)
        rs1 = get_binary_field(word, 19, 15)
        funct3 = get_binary_field(word, 14, 12)
        immediate_bits_4_1 = get_binary_field(word, 11, 8)
        immediate_bit_11 = get_binary_field(word, 7, 7)
        opcode = get_binary_field(word, 6, 0)

        # Se reconstruye el inmediato en el orden lógico:
        # imm[12] | imm[11] | imm[10:5] | imm[4:1] | imm[0].
        immediate = (
            immediate_bit_12
            + immediate_bit_11
            + immediate_bits_10_5
            + immediate_bits_4_1
            + "0"
        )
        immediate_decimal = signed_value(immediate)

        fields = [
            ("imm[12]", "[31]", immediate_bit_12),
            ("imm[10:5]", "[30:25]", immediate_bits_10_5),
            ("rs2", "[24:20]", rs2),
            ("rs1", "[19:15]", rs1),
            ("funct3", "[14:12]", funct3),
            ("imm[4:1]", "[11:8]", immediate_bits_4_1),
            ("imm[11]", "[7]", immediate_bit_11),
            ("opcode", "[6:0]", opcode),
        ]

        explanations = [
            (
                f"imm[12] es el bit de signo. "
                f"El offset completo es {immediate_decimal}."
            ),
            "imm[10:5] contiene parte del offset del branch.",
            f"rs2 = {int(rs2, 2)} (x{int(rs2, 2)}), segundo registro comparado.",
            f"rs1 = {int(rs1, 2)} (x{int(rs1, 2)}), primer registro comparado.",
            "funct3 diferencia beq de bne.",
            "imm[4:1] contiene parte del offset del branch.",
            "imm[11] contiene parte del offset del branch.",
            "opcode identifica una instrucción de formato B.",
        ]

    else:
        raise ValueError(f"Formato desconocido: {instruction_format}")

    # Se calcula la representación binaria completa de 32 bits.
    binary_word = format(word & 0xFFFFFFFF, "032b")

    # Se construye la tabla ASCII con todos los campos.
    table_lines = [
        "+-------------+-----------+--------------+-------------------------------------------------------------------------+",
        "| Campo       | Bits      | Binario      | Significado                                                             |",
        "+-------------+-----------+--------------+-------------------------------------------------------------------------+",
    ]

    for field, (field_name, bit_range, binary_value) in enumerate(fields):
        table_lines.append(
            format_field(
                field_name,
                bit_range,
                binary_value,
                explanations[field]
            )
            + " |"
        )

    table_lines.append(
        "+-------------+-----------+--------------+-------------------------------------------------------------------------+"
    )

    # Se agregan los pasos principales del proceso de codificación.
    result = [
        f"Instrucción: {instruction}",
        f"Formato: {instruction_format}",
        "",
        "Proceso de codificación:",
        "1. Se identifica el mnemónico y sus operandos.",
        "2. Los registros x0 hasta x31 se convierten a valores binarios de 5 bits.",
        "3. Se consultan opcode, funct3 y funct7 en la tabla de la ISA.",
        "4. Los campos se colocan en las posiciones definidas por el formato.",
    ]

    if instruction_format in ["I", "S", "B"]:
        result.append(
            "5. El inmediato negativo se representa usando complemento a dos."
        )

    if instruction_format == "B":
        result.append(
            "6. En formato B, los bits del offset se reorganizan y el bit 0 es cero."
        )

    result.extend([
        "",
        "Cadena binaria completa [31:0]:",
        binary_word,
        "",
        "Campos de la instrucción:",
        *table_lines,
    ])

    return "\n".join(result)
