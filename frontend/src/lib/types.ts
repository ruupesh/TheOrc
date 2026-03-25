// ─── Auth ────────────────────────────────────────────
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

// ─── Chat ────────────────────────────────────────────
export interface HITLApprovalItem {
  function_id: string;
  function_name: string;
  confirmed: boolean;
  payload?: Record<string, unknown>;
}

export interface HITLRequestedItem {
  function_id: string;
  function_name: string;
  confirmed: boolean;
  payload: Record<string, unknown>;
  hint?: string;
}

export interface ChatRequestContent {
  message?: string;
  metadata?: Record<string, unknown>;
  hitl_approval?: HITLApprovalItem[];
}

export interface ChatResponseContent {
  message?: string;
  metadata?: Record<string, unknown>;
  hitl_requested?: HITLRequestedItem[];
}

export interface ChatRequest {
  user_id: string;
  session_id: string;
  content: ChatRequestContent;
}

export interface ChatResponse {
  user_id: string;
  message_id: string;
  session_id: string;
  role: "assistant";
  content: ChatResponseContent;
  timestamp: string;
}

// Local message type for the UI
export interface ChatMessage {
  id: string;
  role: "human" | "assistant";
  content: string;
  timestamp: string;
  hitl_requested?: HITLRequestedItem[];
}

// ─── Agents ──────────────────────────────────────────
export interface Agent {
  id: string;
  owner_id: string;
  name: string;
  description: string;
  host: string;
  port: number;
  agent_card_path: string;
  timeout: number;
  full_history: boolean;
  authentication_flag: boolean;
  allow_conversation_history: boolean;
  is_system: boolean;
  created_at: string;
}

export interface AgentCreate {
  name: string;
  description: string;
  host: string;
  port: number;
  agent_card_path?: string;
  timeout?: number;
  full_history?: boolean;
  authentication_flag?: boolean;
  allow_conversation_history?: boolean;
}

export interface AgentUpdate {
  name?: string;
  description?: string;
  host?: string;
  port?: number;
  agent_card_path?: string;
  timeout?: number;
  full_history?: boolean;
  authentication_flag?: boolean;
  allow_conversation_history?: boolean;
}

// ─── MCP Tools ───────────────────────────────────────
export interface McpTool {
  id: string;
  owner_id: string;
  installed_from_listing_id?: string;
  name: string;
  connection_type: string;
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  url?: string;
  headers?: Record<string, string>;
  sse_read_timeout: number;
  timeout: number;
  authentication_flag: boolean;
  tool_filter?: string[];
  is_system: boolean;
  created_at: string;
}

export interface McpToolCreate {
  name: string;
  connection_type: string;
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  url?: string;
  headers?: Record<string, string>;
  sse_read_timeout?: number;
  timeout?: number;
  authentication_flag?: boolean;
  auth_token?: string;
  tool_filter?: string[];
}

export interface McpToolUpdate {
  name?: string;
  connection_type?: string;
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  url?: string;
  headers?: Record<string, string>;
  sse_read_timeout?: number;
  timeout?: number;
  authentication_flag?: boolean;
  auth_token?: string;
  tool_filter?: string[];
}

// ─── Marketplace ─────────────────────────────────────
export interface MarketplaceListing {
  id: string;
  agent_id?: string;
  mcp_tool_id?: string;
  publisher_id: string;
  publisher_username?: string;
  item_type: "agent" | "mcp_tool";
  visibility: "public" | "private";
  title: string;
  description: string;
  agent_card_url?: string;
  agent_name?: string;
  agent_host?: string;
  agent_port?: number;
  mcp_tool_name?: string;
  mcp_tool_connection_type?: string;
  is_published: boolean;
  created_at: string;
}

export interface MarketplacePublishRequest {
  agent_id?: string;
  mcp_tool_id?: string;
  title: string;
  description: string;
  visibility: "public" | "private";
}

export interface InstallAgentRequest {
  listing_id: string;
}

export interface Installation {
  id: string;
  user_id: string;
  listing_id: string;
  installed_at: string;
  listing?: MarketplaceListing;
}
