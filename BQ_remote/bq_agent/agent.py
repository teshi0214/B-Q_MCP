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


def _get_auth_headers():
    """認証ヘッダーを取得"""
    credentials, project = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/bigquery",
            "https://www.googleapis.com/auth/cloud-platform"
        ]
    )
    
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)
    
    return {
        "Authorization": f"Bearer {credentials.token}",
        "x-goog-user-project": project or PROJECT_ID
    }


# MCPToolset をグローバルで1回だけ初期化
_bigquery_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=BIGQUERY_MCP_URL,
        headers=_get_auth_headers()
    )
)


# エージェント定義
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="bq_remote_agent",
    description="BigQuery データ分析エージェント",
    instruction=f"""あなたはBigQueryのデータ分析エキスパートです。

プロジェクトID: {PROJECT_ID}

## 利用可能なツール
- list_dataset_ids: データセット一覧を取得
- list_table_ids: テーブル一覧を取得  
- get_table_info: テーブルのスキーマ情報を取得
- execute_sql: 任意のSQLクエリを実行

## 重要なルール
1. ユーザーの質問に答えるために必要なツールは、説明なしに即座に実行してください
2. 「〜を取得します」「〜を実行します」と言う前に、まずツールを呼び出してください
3. ツールの結果を待ってから、結果をユーザーに説明してください
4. 1回のレスポンスで複数のツールを連続して呼び出すことができます

## 例
ユーザー: 「テーブル一覧を見せて」
→ すぐに list_table_ids を実行し、結果を表示

ユーザー: 「forecasting_sticker_salesのテーブルは？」
→ すぐに list_table_ids(datasetId="forecasting_sticker_sales") を実行

日本語で分かりやすく回答してください。
""",
    tools=[_bigquery_toolset]
)
