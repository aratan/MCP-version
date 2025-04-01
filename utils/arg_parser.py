import json
import argparse

def create_parser():
    parser = argparse.ArgumentParser(description="Ejecuta un modelo Ollama con funciones personalizadas.")
    parser.add_argument("-m", "--model", default="llama3.2:3b", help="Modelo de Ollama (ej. 'llama3.2:7b')")
    parser.add_argument("-l", "--functions", default="", help="Funciones habilitadas (ej. 'MCP_SUMA,MCP_RESTA')")
    parser.add_argument("-p", "--prompt", default="¿Cuánto es 10 + 10?", help="Prompt del usuario")
    return parser

def parse_and_validate_args(function_name, args_dict, param_mapping):
    """Parses and validates arguments for a given function."""
    try:
        if isinstance(args_dict, str):
            args_dict = json.loads(args_dict)

        mapped_args = {}
        if param_mapping:
            for key, value in args_dict.items():
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                if key in param_mapping:
                    mapped_args[param_mapping[key]] = value
                else:
                    mapped_args[key] = value
        else:
            mapped_args = {
                key: int(value) if isinstance(value, str) and value.isdigit() else value
                for key, value in args_dict.items()
            }

        return mapped_args

    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Error parsing arguments for {function_name}: {e}")
