import ollama
import json
import argparse

def MCP_SUMA(a: int, b: int) -> int:
    """Suma dos números."""
    return a + b

def MCP_RESTA(a: int, b: int) -> int:
    """Resta dos números."""
    return a - b

# --- Configuración de argumentos ---
parser = argparse.ArgumentParser(description="Ejecuta un modelo Ollama con funciones personalizadas.")
parser.add_argument("-m", "--model", default="llama3.2:3b", help="Modelo de Ollama (ej. 'llama3.2:7b')")
parser.add_argument("-l", "--functions", default="MCP_SUMA,MCP_RESTA", help="Funciones habilitadas (ej. 'MCP_SUMA,MCP_RESTA')")
parser.add_argument("-p", "--prompt", default="¿Cuánto es 10 + 10?", help="Prompt del usuario")
args = parser.parse_args()

# --- Habilitar funciones ---
available_functions = {}
if "MCP_SUMA" in args.functions.split(","):
    available_functions["MCP_SUMA"] = MCP_SUMA
if "MCP_RESTA" in args.functions.split(","):
    available_functions["MCP_RESTA"] = MCP_RESTA

# --- Cargar herramientas ---
try:
    with open('MCP-SERVER.json', 'r') as f:
        tools = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error cargando herramientas: {e}")
    exit(1)

# --- Conversación ---
messages = [{"role": "user", "content": args.prompt}]

try:
    # Primera llamada al modelo
    response = ollama.chat(
        model=args.model,
        messages=messages,
        tools=tools,
    )
    messages.append(response["message"])

    # Procesar llamadas a funciones
    if "tool_calls" in response["message"]:
        for tool_call in response["message"]["tool_calls"]:
            function_name = tool_call["function"]["name"]
            # Manejar alias de función de forma insensible a mayúsculas
            if function_name.lower() == "add":
                function_name = "MCP_SUMA"
            elif function_name.lower() in ["subtract", "sub"]:
                function_name = "MCP_RESTA"
            if function_name in available_functions:
                try:
                    # Manejar argumentos (ya sea dict o str)
                    args_dict = tool_call["function"]["arguments"]
                    if isinstance(args_dict, str):
                        args_dict = json.loads(args_dict)
                    # Mapear claves para MCP_RESTA: x->a y y->b
                    if function_name == "MCP_RESTA":
                        if "x" in args_dict:
                            args_dict["a"] = args_dict.pop("x")
                        if "y" in args_dict:
                            args_dict["b"] = args_dict.pop("y")
                    # Convertir valores a enteros
                    args_dict = {k: int(v) for k, v in args_dict.items()}
                    
                    # Ejecutar función
                    result = available_functions[function_name](**args_dict)
                    
                    # Añadir resultado
                    messages.append({
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    })

                    # Obtener respuesta final
                    final_response = ollama.chat(
                        model=args.model,
                        messages=messages,
                    )
                    print(f"\nRESULTADO:\n{final_response['message']['content']}\n")

                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Error en argumentos: {e}")
                except Exception as e:
                    print(f"Error ejecutando {function_name}: {e}")
            else:
                print(f"Función {function_name} no habilitada (use -l para activar)")
    else:
        print(f"\nRESPUESTA DIRECTa:\n{response['message']['content']}\n")

except Exception as e:
    print(f"ERROR: {e}")