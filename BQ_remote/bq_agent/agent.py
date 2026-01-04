"""
BigQuery Remote MCP Server Agent for Agent Engine + Gemini Enterprise

デプロイ方法:
1. adk deploy agent_engine --project=agent-vi-473112 --region=us-central1
2. Gemini EnterpriseでOAuth設定してエージェント登録
"""
import os
import google.auth
from google.auth.transport import requests as google_requests
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# BigQuery Remote MCP Server URL
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp"

# プロジェクトID
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "agent-vi-473112")


def get_bigquery_toolset():
    """
    BigQuery MCP Toolsetを取得
    Agent Engine上ではサービスアカウントの認証情報を使用
    """
    # Application Default Credentials (ADC) を使用
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    
    # トークンをリフレッシュ
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)
    
    # MCP接続ヘッダー
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "x-goog-user-project": project or PROJECT_ID
    }
    
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=headers
        )
    )


# エージェント定義
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="bq_remote_agent",
    description="BigQuery データ分析エージェント",
    instruction=f"""あなたはBigQueryのデータ分析エキスパートです。

プロジェクトID: {PROJECT_ID}

BigQuery MCPツールを使って以下のことができます：
- list_dataset_ids: データセット一覧を取得
- list_table_ids: テーブル一覧を取得  
- get_table_info: テーブルのスキーマ情報を取得
- execute_sql: 任意のSQLクエリを実行

手順:
1. まず list_dataset_ids でデータセットを確認
2. list_table_ids でテーブル一覧を取得
3. get_table_info でスキーマを確認
4. execute_sql で分析クエリを実行

日本語で分かりやすく回答してください。
""",
    tools=[get_bigquery_toolset()]
)
