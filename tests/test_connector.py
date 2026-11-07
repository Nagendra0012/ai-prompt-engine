import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from prompt_engine.workflow import TOPICS

ROOT = Path(__file__).resolve().parents[1]

async def exercise(streams, expected_prefs):
    async with ClientSession(streams[0], streams[1]) as session:
        await session.initialize()
        tools = await session.list_tools()
        assert {tool.name for tool in tools.tools} == {"start_quiz", "prepare_prompt"}
        for category in TOPICS:
            for mode in ("create", "improve"):
                params = {"category": category, "mode": mode}
                result = await session.call_tool("start_quiz", params)
                assert not result.isError
                quiz = json.loads(result.content[0].text)["questions"]
                assert len(quiz) == 3 and all(q["custom_answer_allowed"] for q in quiz)
                answers = [q["choices"][0] for q in quiz]
                answers[1] = "Use my own project evidence"
                source = "Draft my cybersecurity portfolio" if mode == "create" else "Improve my resume for a SOC analyst job"
                response = await session.call_tool("prepare_prompt", {**params, "source": source, "answers": answers})
                assert not response.isError
                brief = json.loads(response.content[0].text)
                assert brief["style_defaults"] == expected_prefs and brief["source"] == source
                assert [q["answer"] for q in brief["quiz_answers"]] == answers
        invalid = await session.call_tool("prepare_prompt", {**params, "source": "Goal", "answers": []})
        assert invalid.isError

class ConnectorTests(unittest.TestCase):
    def test_local(self):
        async def run():
            params = StdioServerParameters(command=sys.executable, args=["-m", "prompt_engine.server"],
                cwd=str(ROOT), env={"PROMPT_ENGINE_PREFERENCES": '{"tone":"direct"}'})
            async with stdio_client(params) as streams:
                await exercise(streams, {"tone": "direct"})
        asyncio.run(run())

    def test_http(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        with subprocess.Popen([sys.executable,"-m","prompt_engine.server","--http","--port",str(port)],
                cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                env={**os.environ, "PROMPT_ENGINE_PREFERENCES": '{"tone":"private"}'}) as process:
            try:
                for _ in range(100):
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=.1):
                            break
                    except OSError:
                        if process.poll() is not None:
                            self.fail("HTTP server exited before accepting connections")
                        time.sleep(.05)
                async def run():
                    async with streamablehttp_client(f"http://127.0.0.1:{port}/mcp") as streams:
                        await exercise(streams, {})
                asyncio.run(run())
            finally:
                process.terminate()
                process.wait(timeout=10)
