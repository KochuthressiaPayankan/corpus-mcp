import asyncio

from mcp import Client

from corpus_mcp.server import mcp


async def attempt(label, coro):
    print(f"\n=== {label}")
    try:
        print(await coro)
    except Exception as exc:
        print("ERROR:", type(exc).__name__, exc)


async def main():
    async with Client(mcp) as client:
        await attempt("resource templates", client.list_resource_templates())
        await attempt("read flat file", client.read_resource("docs://rag-basics.md"))
        await attempt("read nested file", client.read_resource("docs://subfolder/nested.md"))
        await attempt("traversal", client.read_resource("docs://..%2F..%2Fetc%2Fpasswd"))
        await attempt("prompts", client.list_prompts())
        await attempt(
            "get prompt",
            client.get_prompt("summarize_document", {"path": "rag-basics.md"}),
        )


asyncio.run(main())
