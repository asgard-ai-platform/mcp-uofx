import asyncio
import os
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


VALID_TOKEN = os.getenv("MCP_SSE_TEST_TOKEN", "test_token")
VALID_USER = os.getenv("MCP_SSE_TEST_USER", "test_user")

async def run_client_with_token(token: str):
    url = "http://127.0.0.1:8000/sse"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    print(f"\n嘗試連線到 SSE 伺服器 (Token: {token if token else 'None'})")
    
    try:
        # 1. 透過 SSE 建立連線
        async with sse_client(url=url, headers=headers) as (read_stream, write_stream):
            # 2. 啟動 MCP Session 通訊
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("✅ 連線與初始化成功！")
                
                # 3. 列出可用的 Tools
                response = await session.list_tools()
                tools = [tool.name for tool in response.tools]
                print(f"可用的 Tools: {tools}")
                
                # 4. 呼叫測試的 Tool (uofx_test_whoami)
                if "uofx_test_whoami" in tools:
                    print("呼叫 Tool: uofx_test_whoami...")
                    result = await session.call_tool("uofx_test_whoami", {})
                    # 顯示回傳結果 (text_content)
                    print(f"回傳結果: {result.content[0].text}")

    except Exception as e:
        print(f"❌ 連線或執行失敗: {e}")

async def main():
    print("=== 測試 1: 未攜帶 Token (預期失敗 401) ===")
    await run_client_with_token(None)
    
    await asyncio.sleep(1)
    
    print("\n=== 測試 2: 攜帶錯誤 Token (預期失敗 401) ===")
    await run_client_with_token("invalid_token")
    
    await asyncio.sleep(1)
    
    print(f"\n=== 測試 3: 攜帶有效 Token (預期成功辨識為 {VALID_USER}) ===")
    await run_client_with_token(VALID_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
