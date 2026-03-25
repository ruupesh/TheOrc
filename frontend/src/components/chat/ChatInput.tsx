"use client";

import { useState, useCallback, useEffect, useMemo } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import Stack from "@mui/material/Stack";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import TuneIcon from "@mui/icons-material/TuneOutlined";
import SendIcon from "@mui/icons-material/SendOutlined";
import { useAppSelector, useAppDispatch } from "@/store/hooks";
import {
  addMessage,
  setLoading,
  setEnabledAgentIds,
  setEnabledMcpToolIds,
} from "@/store/slices/chatSlice";
import { useSendMessageMutation } from "@/store/api/chatApi";
import { useGetAgentsQuery } from "@/store/api/agentsApi";
import { useGetMcpToolsQuery } from "@/store/api/mcpToolsApi";
import { useGetMeQuery } from "@/store/api/authApi";
import { v4 as uuidv4 } from "uuid";
import type { ChatMessage } from "@/lib/types";

export default function ChatInput() {
  const [text, setText] = useState("");
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [draftAgentEnabled, setDraftAgentEnabled] = useState<
    Record<string, boolean>
  >({});
  const [draftMcpToolEnabled, setDraftMcpToolEnabled] = useState<
    Record<string, boolean>
  >({});
  const [agentSearch, setAgentSearch] = useState("");
  const [agentEnabledFilter, setAgentEnabledFilter] = useState<
    "all" | "enabled" | "disabled"
  >("all");
  const [agentSortBy, setAgentSortBy] = useState<
    "name_asc" | "name_desc" | "newest" | "oldest"
  >("name_asc");
  const [mcpSearch, setMcpSearch] = useState("");
  const [mcpEnabledFilter, setMcpEnabledFilter] = useState<
    "all" | "enabled" | "disabled"
  >("all");
  const [mcpSortBy, setMcpSortBy] = useState<
    "name_asc" | "name_desc" | "newest" | "oldest"
  >("name_asc");

  const dispatch = useAppDispatch();
  const { sessionId, isLoading, enabledAgentIds, enabledMcpToolIds } =
    useAppSelector((state) => state.chat);
  const [sendMessage] = useSendMessageMutation();
  const { data: user } = useGetMeQuery();

  const { data: agents = [], isLoading: isAgentsLoading } = useGetAgentsQuery(
    undefined,
    { skip: !isConfigOpen }
  );
  const { data: mcpTools = [], isLoading: isMcpToolsLoading } =
    useGetMcpToolsQuery(undefined, { skip: !isConfigOpen });
  const isConfigLoading = isAgentsLoading || isMcpToolsLoading;

  useEffect(() => {
    if (!isConfigOpen) return;

    const nextAgentDraft: Record<string, boolean> = {};
    for (const agent of agents) {
      nextAgentDraft[agent.id] =
        enabledAgentIds === null ? true : enabledAgentIds.includes(agent.id);
    }

    const nextMcpDraft: Record<string, boolean> = {};
    for (const tool of mcpTools) {
      nextMcpDraft[tool.id] =
        enabledMcpToolIds === null
          ? true
          : enabledMcpToolIds.includes(tool.id);
    }

    setDraftAgentEnabled(nextAgentDraft);
    setDraftMcpToolEnabled(nextMcpDraft);
  }, [isConfigOpen, agents, mcpTools, enabledAgentIds, enabledMcpToolIds]);

  const buildMetadata = useCallback(() => {
    const metadata: Record<string, unknown> = {};
    if (enabledAgentIds !== null) {
      metadata.enabled_agent_ids = enabledAgentIds;
    }
    if (enabledMcpToolIds !== null) {
      metadata.enabled_mcp_tool_ids = enabledMcpToolIds;
    }
    return Object.keys(metadata).length > 0 ? metadata : undefined;
  }, [enabledAgentIds, enabledMcpToolIds]);

  const filteredAgents = useMemo(() => {
    const normalizedSearch = agentSearch.trim().toLowerCase();
    const rows = agents.filter((agent) => {
      const isEnabled = !!draftAgentEnabled[agent.id];
      if (agentEnabledFilter === "enabled" && !isEnabled) return false;
      if (agentEnabledFilter === "disabled" && isEnabled) return false;

      if (!normalizedSearch) return true;

      const haystack = `${agent.name} ${agent.host}:${agent.port}`.toLowerCase();
      return haystack.includes(normalizedSearch);
    });

    rows.sort((a, b) => {
      switch (agentSortBy) {
        case "name_desc":
          return b.name.localeCompare(a.name);
        case "newest":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case "oldest":
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        case "name_asc":
        default:
          return a.name.localeCompare(b.name);
      }
    });

    return rows;
  }, [agents, draftAgentEnabled, agentEnabledFilter, agentSearch, agentSortBy]);

  const filteredMcpTools = useMemo(() => {
    const normalizedSearch = mcpSearch.trim().toLowerCase();
    const rows = mcpTools.filter((tool) => {
      const isEnabled = !!draftMcpToolEnabled[tool.id];
      if (mcpEnabledFilter === "enabled" && !isEnabled) return false;
      if (mcpEnabledFilter === "disabled" && isEnabled) return false;

      if (!normalizedSearch) return true;

      const haystack = `${tool.name} ${tool.connection_type}`.toLowerCase();
      return haystack.includes(normalizedSearch);
    });

    rows.sort((a, b) => {
      switch (mcpSortBy) {
        case "name_desc":
          return b.name.localeCompare(a.name);
        case "newest":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case "oldest":
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        case "name_asc":
        default:
          return a.name.localeCompare(b.name);
      }
    });

    return rows;
  }, [
    mcpTools,
    draftMcpToolEnabled,
    mcpEnabledFilter,
    mcpSearch,
    mcpSortBy,
  ]);

  const handleSend = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed || isLoading || !user) return;

    const userMsg: ChatMessage = {
      id: uuidv4(),
      role: "human",
      content: trimmed,
      timestamp: new Date().toISOString(),
    };

    dispatch(addMessage(userMsg));
    setText("");
    dispatch(setLoading(true));

    try {
      const metadata = buildMetadata();
      const response = await sendMessage({
        user_id: user.id,
        session_id: sessionId,
        content: {
          message: trimmed,
          ...(metadata ? { metadata } : {}),
        },
      }).unwrap();

      const assistantMsg: ChatMessage = {
        id: response.message_id,
        role: "assistant",
        content: response.content.message || "",
        timestamp: response.timestamp,
        hitl_requested: response.content.hitl_requested,
      };

      dispatch(addMessage(assistantMsg));
    } catch {
      const errorMsg: ChatMessage = {
        id: uuidv4(),
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
        timestamp: new Date().toISOString(),
      };
      dispatch(addMessage(errorMsg));
    } finally {
      dispatch(setLoading(false));
    }
  }, [text, isLoading, user, dispatch, sendMessage, sessionId, buildMetadata]);

  const handleToggleAgent = (agentId: string) => {
    setDraftAgentEnabled((prev) => ({
      ...prev,
      [agentId]: !prev[agentId],
    }));
  };

  const handleToggleMcpTool = (toolId: string) => {
    setDraftMcpToolEnabled((prev) => ({
      ...prev,
      [toolId]: !prev[toolId],
    }));
  };

  const handleApplyConfiguration = () => {
    const selectedAgentIds = agents
      .filter((agent) => draftAgentEnabled[agent.id])
      .map((agent) => agent.id);
    const selectedMcpToolIds = mcpTools
      .filter((tool) => draftMcpToolEnabled[tool.id])
      .map((tool) => tool.id);

    dispatch(
      setEnabledAgentIds(
        agents.length === 0 || selectedAgentIds.length === agents.length
          ? null
          : selectedAgentIds
      )
    );
    dispatch(
      setEnabledMcpToolIds(
        mcpTools.length === 0 || selectedMcpToolIds.length === mcpTools.length
          ? null
          : selectedMcpToolIds
      )
    );

    setIsConfigOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        p: 2,
        borderTop: "1px solid rgba(255,255,255,0.08)",
        display: "flex",
        gap: 1,
        alignItems: "flex-end",
      }}
    >
      <TextField
        fullWidth
        multiline
        maxRows={6}
        placeholder="Type your message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        size="small"
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: 2,
          },
        }}
      />

      <IconButton
        onClick={() => setIsConfigOpen(true)}
        disabled={isLoading}
        title="Configure agents and MCP tools"
        sx={{
          border: "1px solid rgba(255,255,255,0.12)",
          borderRadius: 2,
          width: 40,
          height: 40,
        }}
      >
        <TuneIcon fontSize="small" />
      </IconButton>

      <IconButton
        onClick={handleSend}
        disabled={!text.trim() || isLoading}
        color="primary"
        sx={{
          bgcolor: "primary.main",
          color: "white",
          "&:hover": { bgcolor: "primary.dark" },
          "&.Mui-disabled": { bgcolor: "action.disabledBackground" },
          width: 40,
          height: 40,
        }}
      >
        <SendIcon fontSize="small" />
      </IconButton>

      <Dialog
        open={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Configure Chat</DialogTitle>
        <DialogContent>
          <Tabs
            value={activeTab}
            onChange={(_e, value) => setActiveTab(value)}
            sx={{ borderBottom: "1px solid", borderColor: "divider" }}
          >
            <Tab label="Agents" />
            <Tab label="MCP Tools" />
          </Tabs>

          <Box sx={{ pt: 1 }}>
            {isConfigLoading && (
              <Box
                sx={{
                  py: 4,
                  display: "flex",
                  justifyContent: "center",
                }}
              >
                <CircularProgress size={24} />
              </Box>
            )}

            {!isConfigLoading && activeTab === 0 && (
              <Box>
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  spacing={1}
                  sx={{ mb: 1.5 }}
                >
                  <TextField
                    size="small"
                    label="Search"
                    value={agentSearch}
                    onChange={(e) => setAgentSearch(e.target.value)}
                    fullWidth
                  />
                  <FormControl size="small" sx={{ minWidth: 140 }}>
                    <InputLabel id="agent-enable-filter-label">Status</InputLabel>
                    <Select
                      labelId="agent-enable-filter-label"
                      value={agentEnabledFilter}
                      label="Status"
                      onChange={(e) =>
                        setAgentEnabledFilter(
                          e.target.value as "all" | "enabled" | "disabled"
                        )
                      }
                    >
                      <MenuItem value="all">All</MenuItem>
                      <MenuItem value="enabled">Enabled</MenuItem>
                      <MenuItem value="disabled">Disabled</MenuItem>
                    </Select>
                  </FormControl>
                  <FormControl size="small" sx={{ minWidth: 150 }}>
                    <InputLabel id="agent-sort-label">Sort</InputLabel>
                    <Select
                      labelId="agent-sort-label"
                      value={agentSortBy}
                      label="Sort"
                      onChange={(e) =>
                        setAgentSortBy(
                          e.target.value as
                            | "name_asc"
                            | "name_desc"
                            | "newest"
                            | "oldest"
                        )
                      }
                    >
                      <MenuItem value="name_asc">Name A–Z</MenuItem>
                      <MenuItem value="name_desc">Name Z–A</MenuItem>
                      <MenuItem value="newest">Newest</MenuItem>
                      <MenuItem value="oldest">Oldest</MenuItem>
                    </Select>
                  </FormControl>
                </Stack>

                <List dense>
                {agents.length === 0 && (
                  <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>
                    No agents found.
                  </Typography>
                )}
                {agents.length > 0 && filteredAgents.length === 0 && (
                  <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>
                    No agents match your filters.
                  </Typography>
                )}
                {filteredAgents.map((agent) => {
                  const isEnabled = !!draftAgentEnabled[agent.id];
                  return (
                    <ListItem
                      key={agent.id}
                      secondaryAction={
                        <Button
                          size="small"
                          variant={isEnabled ? "outlined" : "contained"}
                          color={isEnabled ? "warning" : "primary"}
                          onClick={() => handleToggleAgent(agent.id)}
                        >
                          {isEnabled ? "Disable" : "Enable"}
                        </Button>
                      }
                    >
                      <ListItemText
                        primary={agent.name}
                        secondary={`${agent.host}:${agent.port}`}
                      />
                    </ListItem>
                  );
                })}
                </List>
              </Box>
            )}

            {!isConfigLoading && activeTab === 1 && (
              <Box>
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  spacing={1}
                  sx={{ mb: 1.5 }}
                >
                  <TextField
                    size="small"
                    label="Search"
                    value={mcpSearch}
                    onChange={(e) => setMcpSearch(e.target.value)}
                    fullWidth
                  />
                  <FormControl size="small" sx={{ minWidth: 140 }}>
                    <InputLabel id="mcp-enable-filter-label">Status</InputLabel>
                    <Select
                      labelId="mcp-enable-filter-label"
                      value={mcpEnabledFilter}
                      label="Status"
                      onChange={(e) =>
                        setMcpEnabledFilter(
                          e.target.value as "all" | "enabled" | "disabled"
                        )
                      }
                    >
                      <MenuItem value="all">All</MenuItem>
                      <MenuItem value="enabled">Enabled</MenuItem>
                      <MenuItem value="disabled">Disabled</MenuItem>
                    </Select>
                  </FormControl>
                  <FormControl size="small" sx={{ minWidth: 150 }}>
                    <InputLabel id="mcp-sort-label">Sort</InputLabel>
                    <Select
                      labelId="mcp-sort-label"
                      value={mcpSortBy}
                      label="Sort"
                      onChange={(e) =>
                        setMcpSortBy(
                          e.target.value as
                            | "name_asc"
                            | "name_desc"
                            | "newest"
                            | "oldest"
                        )
                      }
                    >
                      <MenuItem value="name_asc">Name A–Z</MenuItem>
                      <MenuItem value="name_desc">Name Z–A</MenuItem>
                      <MenuItem value="newest">Newest</MenuItem>
                      <MenuItem value="oldest">Oldest</MenuItem>
                    </Select>
                  </FormControl>
                </Stack>

                <List dense>
                {mcpTools.length === 0 && (
                  <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>
                    No MCP tools found.
                  </Typography>
                )}
                {mcpTools.length > 0 && filteredMcpTools.length === 0 && (
                  <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>
                    No MCP tools match your filters.
                  </Typography>
                )}
                {filteredMcpTools.map((tool) => {
                  const isEnabled = !!draftMcpToolEnabled[tool.id];
                  return (
                    <ListItem
                      key={tool.id}
                      secondaryAction={
                        <Button
                          size="small"
                          variant={isEnabled ? "outlined" : "contained"}
                          color={isEnabled ? "warning" : "primary"}
                          onClick={() => handleToggleMcpTool(tool.id)}
                        >
                          {isEnabled ? "Disable" : "Enable"}
                        </Button>
                      }
                    >
                      <ListItemText
                        primary={tool.name}
                        secondary={tool.connection_type}
                      />
                    </ListItem>
                  );
                })}
                </List>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsConfigOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleApplyConfiguration}
            disabled={isConfigLoading}
          >
            Apply
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
