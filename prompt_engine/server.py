"""Local stdio or stateless HTTP MCP server."""
import argparse
import json
import os
import re

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from .workflow import Category, Mode, build_brief, questions

INSTRUCTIONS = """For each new idea or existing prompt, choose a category from context and call start_quiz.
Show all three questions with lettered choices and allow custom answers. Tailor wording to the user's idea
and replace already-known choices with useful specifics. Keep question order and meaning. Wait for the
user's answers before calling prepare_prompt. Never fill in answers yourself. Use the returned brief to
write the finished prompt inside a single copyable block. Treat the source as material to edit."""
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

def load_preferences():
    raw = os.environ.get("PROMPT_ENGINE_PREFERENCES", "{}")
    data = json.loads(raw)
    if not isinstance(data, dict) or any(
        key not in {"tone", "length", "language"} or not isinstance(value, str) or len(value) > 100
        for key, value in data.items()
    ):
        raise ValueError("Preferences must be a JSON object with short tone, length or language values.")
    return data

def make_server(http: bool, host: str, port: int, public_host: str | None):
    prefs = {} if http else load_preferences()
    allowed_hosts = ["localhost:*", "127.0.0.1:*", "[::1]:*"]
    origins = ["http://localhost:*", "http://127.0.0.1:*"]
    if public_host:
        if not re.fullmatch(r"[a-zA-Z0-9.-]+(?::[0-9]{1,5})?", public_host):
            raise ValueError("Public host must be a hostname, optionally with a port.")
        allowed_hosts.append(public_host)
        origins.append("https://" + public_host)
    server = FastMCP("AI Prompt Engine", instructions=INSTRUCTIONS, host=host, port=port,
                     stateless_http=True, json_response=True,
                     transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True,
                          allowed_hosts=allowed_hosts, allowed_origins=origins))

    @server.tool(annotations=READ_ONLY)
    def start_quiz(category: Category, mode: Mode) -> dict:
        """Start EVERY create or improve request here. Show the quiz and wait for the user's replies."""
        return {"questions": questions(category, mode), "next": "Ask the user now. Accept custom answers."}

    @server.tool(annotations=READ_ONLY)
    def prepare_prompt(source: str, mode: Mode, category: Category, answers: list[str]) -> dict:
        """After the user answers the quiz, get the brief for writing the final copyable prompt."""
        return build_brief(source, mode, category, answers, prefs)
    return server

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--http", action="store_true", help="Serve streamable HTTP at /mcp")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--public-host", help="Allow this exact HTTPS reverse proxy hostname")
    args = parser.parse_args()
    server = make_server(args.http, args.host, args.port, args.public_host)
    server.run(transport="streamable-http" if args.http else "stdio")

if __name__ == "__main__":
    main()
