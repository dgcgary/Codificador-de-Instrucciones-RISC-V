#!/usr/bin/env python3

import re
import subprocess
import sys
import tempfile
from pathlib import Path


# Herramientas oficiales de RISC-V.
TOOLCHAIN = "riscv64-unknown-elf-gcc"
OBJDUMP = "riscv64-unknown-elf-objdump"

# Rutas principales del proyecto.
PROJECT_DIR = Path(__file__).resolve().parent
RUN_SCRIPT = PROJECT_DIR / "run.sh"


# Tres casos por cada una de las 12 instrucciones soportadas.
CASES = [
    # Formato R: registros variados y uso de x0
    ("add", "add x5, x6, x7"),
    ("add", "add x0, x31, x1"),
    ("add", "add x31, x0, x0"),
    ("sub", "sub x5, x7, x18"),
    ("sub", "sub x0, x28, x0"),
    ("sub", "sub x31, x0, x13"),
    ("and", "and x25, x16, x22"),
    ("and", "and x0, x24, x4"),
    ("and", "and x31, x0, x0"),
    ("or", "or x18, x29, x9"),
    ("or", "or x0, x1, x23"),
    ("or", "or x31, x0, x0"),

    # Formato I aritmético: positivo, negativo y límite
    ("addi", "addi x5, x25, 2035"),
    ("addi", "addi x7, x27, -1"),
    ("addi", "addi x0, x0, -2048"),
    ("andi", "andi x30, x1, 2047"),
    ("andi", "andi x8, x3, -1"),
    ("andi", "andi x31, x0, -2048"),

    # Formato I de carga: offsets positivos, negativos y límite
    ("lw", "lw x30, 8(x14)"),
    ("lw", "lw x29, -1049(x30)"),
    ("lw", "lw x0, 2047(x0)"),
    ("lb", "lb x25, 1705(x27)"),
    ("lb", "lb x18, -1973(x17)"),
    ("lb", "lb x31, -2048(x0)"),

    # Formato S: offsets positivos, negativos y límite
    ("sw", "sw x31, 1774(x31)"),
    ("sw", "sw x16, -411(x23)"),
    ("sw", "sw x0, -2048(x0)"),
    ("sb", "sb x18, 1701(x20)"),
    ("sb", "sb x6, -1(x28)"),
    ("sb", "sb x31, 2047(x0)"),

    # Formato B: offset positivo, negativo y cero
    ("beq", "beq x31, x23, 16"),
    ("beq", "beq x30, x4, -80"),
    ("beq", "beq x0, x0, 0"),
    ("bne", "bne x17, x22, 20"),
    ("bne", "bne x5, x0, -60"),
    ("bne", "bne x0, x0, 0"),
]


def run_command(command):
    """Ejecuta un comando externo y devuelve su salida."""
    result = subprocess.run(
        command,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Comando fallido:\n"
            f"{' '.join(command)}\n\n"
            f"{result.stderr.strip()}"
        )

    return result.stdout


def get_toolchain_hex(object_file):
    """
    Obtiene el código hexadecimal de la instrucción ubicada en la dirección 0.
    """

    output = run_command([
        OBJDUMP,
        "-d",
        "-M",
        "no-aliases",
        str(object_file)
    ])

    # Busca la dirección 0 seguida de una instrucción de 32 bits.
    match = re.search(
        r"^\s*0:\s+([0-9a-fA-F]{8})\b",
        output,
        re.MULTILINE
    )

    if not match:
        raise RuntimeError(
            f"No se encontró una instrucción en la dirección 0:\n{output}"
        )

    return f"0x{match.group(1).lower()}"


def get_model_hex(instruction):
    """Obtiene el código hexadecimal producido por run.sh."""

    output = run_command([
        "bash",
        str(RUN_SCRIPT),
        instruction
    ])

    # Busca la línea obligatoria: HEX: 0xXXXXXXXX.
    match = re.search(
        r"^HEX:\s*(0x[0-9a-fA-F]{8})$",
        output,
        re.MULTILINE
    )

    if not match:
        raise RuntimeError(
            f"No se encontró una línea HEX válida para:\n{instruction}\n"
            f"Salida obtenida:\n{output}"
        )

    return match.group(1).lower()


def create_assembly(instruction, assembly_file):
    """
    Crea el archivo .s correspondiente.

    Para beq y bne, GNU assembler acepta expresiones relativas usando
    el punto actual: .+16, .-80 o .+0.
    """

    if instruction.startswith(("beq ", "bne ")):
        # Separa los operandos del offset numérico.
        branch_without_offset, offset_text = instruction.rsplit(",", 1)
        offset = int(offset_text.strip())

        # Agrega explícitamente el signo al desplazamiento.
        relative_target = f".{offset:+d}"

        assembly = (
            ".section .text\n"
            f"{branch_without_offset}, {relative_target}\n"
        )

        assembly_file.write_text(
            assembly,
            encoding="utf-8"
        )

        return

    # Las instrucciones que no son branches se escriben directamente.
    assembly_file.write_text(
        ".section .text\n"
        f"{instruction}\n",
        encoding="utf-8"
    )


def validate_case(case_number, category, instruction, temporary_dir):
    """
    Ensambla una instrucción y compara objdump contra el modelo.
    """

    # Archivos temporales del caso actual.
    assembly_file = temporary_dir / f"case_{case_number}.s"
    object_file = temporary_dir / f"case_{case_number}.o"

    # Genera el archivo ensamblador.
    create_assembly(
        instruction,
        assembly_file
    )

    # Ensambla usando RV32I y la ABI ILP32.
    run_command([
        TOOLCHAIN,
        "-march=rv32i",
        "-mabi=ilp32",
        "-c",
        str(assembly_file),
        "-o",
        str(object_file)
    ])

    # Obtiene ambos códigos para compararlos.
    official_hex = get_toolchain_hex(object_file)
    model_hex = get_model_hex(instruction)

    status = "OK" if official_hex == model_hex else "ERROR"

    print(
        f"{case_number:02d} | {category:<5} | "
        f"{instruction:<25} | "
        f"modelo: {model_hex} | "
        f"objdump: {official_hex} | {status}"
    )

    return status == "OK"


def main():
    """Ejecuta los 36 casos de validación."""

    # Verifica que las herramientas estén instaladas.
    try:
        run_command([TOOLCHAIN, "--version"])
        run_command([OBJDUMP, "--version"])
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    passed = 0

    print(
        "Caso | Tipo  | Instrucción               | "
        "Modelo        | Objdump       | Resultado"
    )
    print("-" * 105)

    # La carpeta temporal se elimina automáticamente al finalizar.
    with tempfile.TemporaryDirectory(
        prefix="riscv_validation_"
    ) as directory:
        temporary_dir = Path(directory)

        for case_number, (category, instruction) in enumerate(
            CASES,
            start=1
        ):
            try:
                if validate_case(
                    case_number,
                    category,
                    instruction,
                    temporary_dir
                ):
                    passed += 1

            except RuntimeError as error:
                print(
                    f"{case_number:02d} | {category:<5} | "
                    f"{instruction:<25} | ERROR: {error}"
                )

    failed = len(CASES) - passed

    print("-" * 105)
    print(
        f"Total: {len(CASES)} | "
        f"Correctos: {passed} | "
        f"Fallos: {failed}"
    )

    # Código 1 indica que hubo al menos una prueba fallida.
    if failed != 0:
        sys.exit(1)


if __name__ == "__main__":
    main()