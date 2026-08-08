# Workspace Agent Configuration

> [!IMPORTANT]
> This project automatically inherits and enforces all Global Agent Rules from `C:\Users\arfan\.gemini\config\AGENTS.md`.

## Mandatory Project Directives
1. **Auto-Apply Global Rules**: Global rules and skills strictly bind to all operations in this workspace.
2. **Auto-Run MCP Tools on Code Mutations (Existing & Newly Added)**:
   - Every code modification automatically triggers all existing (`sequential-thinking`, `codegraph`, `context7`, `memory`) and any newly registered MCP tools adaptively.
   - Newly added MCP tools in `mcp_config.json` or system environment automatically turn ON and execute on every code mutation without manual configuration.
   - Code mutations, entity signatures, and architectural updates are automatically saved to the persistent `memory` MCP knowledge graph (`create_entities`, `add_observations`).
3. **Adaptive Python/Streamlit Architecture**:
   - Detect and adapt dynamically to Python, Streamlit, Pandas, Scikit-Learn, and financial data tools in this project.
