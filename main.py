import ollama
from functions import *
from utils.arg_parser import create_parser, parse_and_validate_args
from utils.function_manager import FunctionManager

def main():
    # Setup argument parser
    parser = create_parser()
    args = parser.parse_args()

    # Initialize function manager
    function_manager = FunctionManager()
    function_manager.load_config('MCP-SERVER.json')
    function_manager.setup_functions(functions_module=__import__('functions'),
                                   enabled_functions=args.functions.split(",") if args.functions else None)

    # --- Conversation ---
    messages = [{"role": "user", "content": args.prompt}]

    try:
        # First call to the model: pass 'tools' only if functions are enabled
        if function_manager.tools_config and args.functions:
            tools = [{"type": "function", **tool} for tool in function_manager.tools_config]
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
                
                # Resolve alias dynamically using the new method name
                canonical_name = function_manager.resolve_alias(function_name)
                
                if canonical_name and canonical_name in function_manager.available_functions:
                    try:
                        # Use the argument parsing function
                        param_mapping = function_manager.param_map.get(canonical_name, {})
                        args_dict = tool_call["function"]["arguments"]
                        processed_args = parse_and_validate_args(canonical_name, args_dict, param_mapping)
                        
                        # Execute function
                        result = function_manager.available_functions[canonical_name](**processed_args)

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

if __name__ == "__main__":
    main()