import ollama
import json
import argparse
import importlib  # Import the importlib module

# --- Mathematical Functions ---
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

# --- New Function: READ_FILE ---
def READ_FILE(file_path: str) -> str:
    """Reads the content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Ejecuta un modelo Ollama con funciones personalizadas.")
parser.add_argument("-m", "--model", default="llama3.2:3b", help="Modelo de Ollama (ej. 'llama3.2:7b')")
parser.add_argument("-l", "--functions", default="", help="Funciones habilitadas (ej. 'MCP_SUMA,MCP_RESTA')")
parser.add_argument("-p", "--prompt", default="¿Cuánto es 10 + 10?", help="Prompt del usuario")
args = parser.parse_args()

# --- Function to handle argument parsing and validation ---
def parse_and_validate_args(function_name, args_dict, param_mapping):
    """
    Parses and validates arguments for a given function.
    """
    print(f"Function Name: {function_name}")  # Debugging print
    print(f"Original Args Dict: {args_dict}")  # Debug original args
    print(f"Param Mapping: {param_mapping}")  # Debugging print
    
    try:
        if isinstance(args_dict, str):
            args_dict = json.loads(args_dict)

        # Apply parameter mapping if it exists
        mapped_args = {}
        if param_mapping:
            for key, value in args_dict.items():
                # Convert string values to integers for numeric operations
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                # If this key should be mapped, use the mapped name
                if key in param_mapping:
                    mapped_args[param_mapping[key]] = value
                else:
                    mapped_args[key] = value
        else:
            # Convert values even when there's no mapping
            mapped_args = {
                key: int(value) if isinstance(value, str) and value.isdigit() else value
                for key, value in args_dict.items()
            }

        print(f"Mapped Args Dict: {mapped_args}")  # Debug mapped args
        return mapped_args

    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Error parsing arguments for {function_name}: {e}")

# --- Load tools from JSON ---
try:
    with open('MCP-SERVER.json', 'r') as f:
        tools_config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading tools configuration: {e}")
    exit(1)

# --- Build available functions and alias map ---
available_functions = {}
ALIAS_MAP = {}
PARAM_MAP = {}

for tool in tools_config:
    function_name = tool["name"]
    aliases = tool.get("aliases", [])
    param_maps = tool.get("param_maps", {})

    # Add function to available_functions (assuming they are already defined)
    if function_name in globals() or function_name == "READ_FILE":
        if function_name in globals():
            available_functions[function_name] = globals()[function_name]
        elif function_name == "READ_FILE":
            available_functions[function_name] = READ_FILE
        ALIAS_MAP[function_name] = aliases
        PARAM_MAP[function_name] = param_maps
    else:
        print(f"Warning: Function {function_name} not defined in the script.")

# --- Filter available functions based on -l argument ---
if args.functions:
    enabled_functions = [func for func in args.functions.split(",") if func.strip()]
    available_functions = {
        name: func for name, func in available_functions.items()
        if name in enabled_functions
    }

# --- Conversation ---
messages = [{"role": "user", "content": args.prompt}]

try:
    # First call to the model: pass 'tools' only if functions are enabled
    if tools_config and args.functions:
        tools = [{"type": "function", **tool} for tool in tools_config]
        response = ollama.chat(
            model=args.model,
            messages=messages,
            tools=tools,
        )
    else:
        response = ollama.chat(
            model=args.model,
            messages=messages,
        )
    messages.append(response["message"])

    # Process function calls only if functions are enabled
    if args.functions and "tool_calls" in response["message"]:
        for tool_call in response["message"]["tool_calls"]:
            print(f"Tool Call: {tool_call}") # Debugging print
            function_name = tool_call["function"]["name"]
            
            # Resolve alias dynamically
            canonical_name = next(
                (canonical for canonical, aliases in ALIAS_MAP.items()
                 if function_name.lower() in [alias.lower() for alias in aliases]),
                function_name  # Use original function_name as default
            )
            
            if canonical_name and canonical_name in available_functions:
                try:
                    # Use the argument parsing function
                    param_mapping = PARAM_MAP.get(canonical_name, {})
                    args_dict = tool_call["function"]["arguments"]
                    processed_args = parse_and_validate_args(canonical_name, args_dict, param_mapping)
                    
                    # Execute function
                    result = available_functions[canonical_name](**processed_args)

                    # Add result to messages
                    messages.append({
                        "role": "tool",
                        "name": canonical_name,
                        "content": str(result),
                    })

                    # Get final response
                    final_response = ollama.chat(
                        model=args.model,
                        messages=messages,
                    )
                    print(f"\nRESULTADO:\n{final_response['message']['content']}\n")

                except ValueError as e:
                    print(f"Error in arguments: {e}")
                except Exception as e:
                    print(f"Error executing {canonical_name}: {e}")
            else:
                print(f"Función {function_name} no habilitada o no encontrada (use -l para activar)")
    else:
        print(f"\nRESPUESTA DIRECTa:\n{response['message']['content']}\n")

except Exception as e:
    print(f"ERROR: {e}")