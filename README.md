# AI Prompt Engine

AI Prompt Engine is a Model Context Protocol (MCP) connector that helps you turn an idea into a prompt or improve a draft. Start with a request like “help me build a portfolio.” Your AI assistant asks three short questions, then uses your answers to write one prompt you can copy into ChatGPT, Claude, Gemini, or another AI tool. The connector uses your existing assistant and requires no separate model API key.

Try **“Use AI Prompt Engine to create a portfolio prompt for an entry-level cloud security role.”** The quiz asks who will read the portfolio, what proof to feature, and whether you want a working site, copy, or a design. For a rewrite, try **“Use AI Prompt Engine to improve this prompt: Write my resume for a SOC analyst role.”** The last question asks what you want changed.

Built-in quizzes cover resumes, applications, websites, portfolios, coding, cybersecurity, writing, research and a general-purpose category.

## Three ways to guide the quiz

- **Bring an example.** Supply your idea or prompt and label the excerpt you like. Choose which qualities to reuse, such as its structure or level of detail. Names, numbers and claims from the example are excluded unless you independently provide them as facts.
- **Repair an unsatisfactory answer.** Paste the original prompt and the unwanted AI response separately. The quiz asks what went wrong. Your assistant turns your diagnosis into an instruction for a new prompt. The old answer provides evidence of the failure, not facts about you.
- **Resolve a tradeoff.** If two of your requirements compete, the assistant identifies the pair before starting the quiz. One question asks which to prioritize. Choose either requirement or give a custom compromise. A priority you already specified needs no new decision.

For example, paste: “Improve my original prompt: Write a one-page cover letter and include every detail from my resume. Previous answer: It says I led a 12-person incident response team, which I never did. Style example: I like this sample’s short paragraphs.” The three questions cover the inaccurate claim, the sample quality to reuse, and the length-versus-detail priority.

For MCP clients, both tools accept the same optional inputs: `example`, `previous_output` (improve mode), and `competing_requirements` (two concise strings). The host identifies conflicts in the original request; the connector builds the questions and records the user's resolution. Repeat the same inputs in both calls so the answers match their questions. These inputs are request-scoped. Original calls without them still work.

## Run it on your computer

Use Python 3.11 or newer. Clone the repository and open it in a terminal. You can also download the source ZIP and extract it.

```sh
git clone https://github.com/Nagendra0012/ai-prompt-engine.git
cd ai-prompt-engine
```

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\ai-prompt-engine.exe --help
```

**macOS or Linux**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/ai-prompt-engine --help
```

Installing requires access to the Python package index. Normal local operation uses the standard input/output connection between the AI client and the connector.

## Connect an AI client

| Client | Setup |
| --- | --- |
| Claude Desktop or another local MCP client | Add the local command below to the client's MCP server configuration, restart the client and enable the tools. |
| Gemini CLI | Use the same configuration in your Gemini CLI settings. Alternatively, with uv installed and on PATH, run `gemini extensions install .` from the extracted folder or pass the repository URL from an account with access. |
| ChatGPT with custom MCP apps or Claude with remote connector support | Run the HTTP service behind an HTTPS reverse proxy reachable by the client. Add its complete HTTPS URL ending in `/mcp` in the client's custom app or connector settings. Availability depends on the account and workspace. |
| AI tools without a custom connector option, including a Gemini chat surface without MCP access | Paste the instructions from `PORTABLE.md` into a new conversation. |

Example Windows configuration for Claude Desktop or Gemini CLI. Replace the command with the actual absolute path on your machine. On macOS or Linux, use the absolute path to `.venv/bin/ai-prompt-engine`.

```json
{
  "mcpServers": {
    "ai-prompt-engine": {
      "command": "C:\\Projects\\ai-prompt-engine\\.venv\\Scripts\\ai-prompt-engine.exe"
    }
  }
}
```

After reconnecting, ask the assistant to use **AI Prompt Engine**. It should show three questions and wait for you to answer before returning a copyable prompt. Tool output is a writing brief. The host turns it into the final prompt. Quiz behavior depends on that host following the tool instructions.

## Optional memory

The default is fresh each time. The connector does not write ideas, resumes, personal details, answers or prompts to disk. The AI client may keep its own chat history. To reuse style preferences on your computer, add this field alongside `command` in the local client configuration.

```json
"env": {
  "PROMPT_ENGINE_PREFERENCES": "{\"tone\":\"conversational\",\"length\":\"concise\",\"language\":\"English\"}"
}
```

Edit or remove this field and restart the client to change or forget those defaults. Use style preferences only. HTTP mode ignores local preferences so another user cannot inherit yours.

## Remote HTTPS setup

From an activated environment, run this behind an HTTPS reverse proxy on your own host. Replace the example hostname with the one you control.

```sh
ai-prompt-engine --http --host 127.0.0.1 --port 8000 --public-host prompts.example.org
```

Forward `https://prompts.example.org/mcp` to `http://127.0.0.1:8000/mcp` and preserve the Host header. Paste the **HTTPS endpoint** into a compatible remote client. The GitHub repository URL distributes the source. It does not run the server. An endpoint needs to be reachable whenever someone uses it. This sample has no built-in authentication. Anyone who can reach it can use the two stateless tools. For restricted access, supply authentication supported by your client at your gateway. Check proxy logging if processing private material. Local stdio is the simplest personal setup.

## Verify

```sh
python -m unittest discover -s tests
```

The tests run the server as a subprocess, connect using the MCP SDK, and exercise both workflows for every category over stdio and streamable HTTP. They also check incomplete quiz answers and isolation of local preferences. A live model response requires an AI client.

Client documentation: [Claude Desktop MCP setup](https://modelcontextprotocol.io/docs/develop/connect-local-servers), [Gemini CLI MCP servers](https://geminicli.com/docs/tools/mcp-server/), [ChatGPT developer mode](https://platform.openai.com/docs/guides/developer-mode).
