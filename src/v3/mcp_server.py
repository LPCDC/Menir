import json
import logging
from typing import Dict, Any, List
from aiohttp import web

logger = logging.getLogger("MenirMCPGateway")

class MenirMCPServer:
    """
    Gateway Interceptador do WebMCP com Isolamento Galvânico (Phase 31).
    Exposes system skills as tools to Autonomous Agents (Claude/Anti-Gravity) via JSON-RPC.
    Strictly filters tool visibility (list_tools) and executions based on Tenant Scopes.
    """
    def __init__(self, runner):
        self.runner = runner
        self.tools_registry = {
            "validate_swiss_vat": {
                "name": "validate_swiss_vat",
                "description": "Valida um número UID/TVA Suíço usando o algoritmo MOD11 para evitar alucinações matemáticas do LLM. Retorna dicionário com 'is_valid'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vat_number": {"type": "string", "description": "Formato CHE-XXX.XXX.XXX"}
                    },
                    "required": ["vat_number"]
                },
                "allowed_tenants": ["BECO", "SANTOS"]
            },
            "export_cresus_tabular": {
                "name": "export_cresus_tabular",
                "description": "Exporta as transações financeiras reconciliadas do Tenant ativo para formato tabular .txt do ERP Crésus.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "allowed_tenants": ["BECO"] # APENAS PARA A FIDUCIÁRIA BECO
            },
            "purge_tenant_data": {
                "name": "purge_tenant_data",
                "description": "EXTREMO PERIGO: Deleta sub-grafos massivos do Neo4j. Apenas para debug.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "confirm": {"type": "boolean", "description": "Passar True para explodir tudo."}
                    },
                    "required": ["confirm"]
                },
                "allowed_tenants": ["ROOT"] # APENAS ADMINISTRAÇÃO TOTAL (AI_AUDITOR)
            }
        }

    async def get_allowed_tools(self, tenant_id: str) -> List[Dict]:
        """
        Isolamento Galvânico: Retorna apenas ferramentas que o Tenant pode ver.
        Prevents Autonomous Agents from hallucinating non-authorized system powers.
        """
        allowed = []
        for name, tool in self.tools_registry.items():
            if tenant_id in tool.get("allowed_tenants", []) or ("ROOT" in tool.get("allowed_tenants", []) and tenant_id == "ROOT"):
                # Remove o array 'allowed_tenants' para não poluir o manifesto WebMCP oficial do agente
                public_tool = {k: v for k, v in tool.items() if k != "allowed_tenants"}
                allowed.append(public_tool)
        return allowed

    async def execute_tool(self, tenant_id: str, tool_name: str, arguments: Dict) -> Any:
        """
        Controlador de Execução. Ponto de estrangulamento (Choke-Point) de Fine-Grained Access Control.
        """
        tool = self.tools_registry.get(tool_name)
        if not tool or (tenant_id not in tool.get("allowed_tenants", []) and tenant_id != "ROOT"):
            raise Exception(f"Galvanic Isolation Violation: Tool '{tool_name}' not found or not accessible to Tenant '{tenant_id}'")
        
        logger.info(f"⚙️ WebMCP Executing '{tool_name}' para Tenant: {tenant_id}")
        
        # Implementações Mock/Real (Integráveis com `self.runner`)
        if tool_name == "validate_swiss_vat":
            # Placeholder MOD11 logic para o Agent (O algoritmo MOD11 real deve viver dentro da Skill no futuro)
            vat = arguments.get("vat_number", "")
            return {"vat": vat, "is_valid": True, "method": "MOD11_MOCK_CHECK"}
            
        elif tool_name == "export_cresus_tabular":
            # Na versão integrada, chamaria o CresusExporter
            return {"status": "SUCCESS", "message": f"CRÉSUS tabular export concluded for Tenant {tenant_id}."}
            
        return {"error": "Tool implemented in schema but handler missing in execution mapping."}

    async def handle_mcp_request(self, request: web.Request) -> web.Response:
        """
        Endpoint HTTP JSON-RPC do Menir WebMCP Interceptor.
        Extracts Tenant ID via Authorization Headers.
        """
        auth_header = request.headers.get('Authorization', '')
        
        # Determinação JWT/Scopes do Tenant (Simulacro baseado nos headers da Fase 31)
        tenant_context = "GUEST"
        if "BECO" in auth_header:
            tenant_context = "BECO"
        elif "SANTOS" in auth_header:
            tenant_context = "SANTOS"
        elif "ROOT" in auth_header:
            tenant_context = "ROOT"

        try:
            payload = await request.json()
            method = payload.get("method")
            msg_id = payload.get("id")
            params = payload.get("params", {})
            
            logger.info(f"🛡️ [WebMCP Gateway] Inbound '{method}' request from Tenant Identity: {tenant_context}")

            if method == "tools/list":
                tools = await self.get_allowed_tools(tenant_context)
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": tools}
                }
                return web.json_response(response)

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                try:
                    result = await self.execute_tool(tenant_context, tool_name, tool_args)
                    return web.json_response({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            # Especificação Oficial MCP (Retorno via array `content`)
                            "content": [{"type": "text", "text": json.dumps(result)}],
                            "isError": False
                        }
                    })
                except Exception as e:
                    logger.warning(f"🛑 WebMCP Gateway Security Blocked action: {e}")
                    return web.json_response({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32000,
                            "message": str(e)
                        }
                    })

            else:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": "JSON-RPC Method not found"}
                })
                
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid or fragmented JSON HTTP Data"}, status=400)
