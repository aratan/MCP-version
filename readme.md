# MCP
## my version

* Usae:

python main.py -m "llama3.2:3b" -l "MCP_SUMA,MCP_RESTA" -p "¿Cuánto es 10 + 15?" 

python main.py -m "llama3.2:3b" -p "¿En que pais esta Madrid?" 

python main.py -m "llama3.2:3b" -l "MCP_SUMA,MCP_RESTA" -p "¿Cuánto es 10 - 15?" 

python main.py -l READ_FILE -p "Por favor, lee el contenido del archivo d:\\agentes\\MCP-SERVER.json"

-m "modelo a usar que acepte tools"
-l "la herramienta a la que llamar"
-p "Prompt"