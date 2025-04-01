def MCP_SUMA(a: int, b: int) -> int:
    """Suma dos números."""
    return a + b

def MCP_RESTA(a: int, b: int) -> int:
    """Resta dos números."""
    return a - b

def MCP_MULTIPLICACION(a: int, b: int) -> int:
    """Multiplica dos números."""
    return a * b

def MCP_DIVISION(a: int, b: int) -> int:
    """Divide dos números (división entera)."""
    if b == 0:
        raise ValueError("División por cero")
    return a // b
