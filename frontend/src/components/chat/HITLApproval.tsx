"use client";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import type { HITLRequestedItem, ChatMessage } from "@/lib/types";
import { useAppSelector, useAppDispatch } from "@/store/hooks";
import { addMessage, setLoading } from "@/store/slices/chatSlice";
import { useSendMessageMutation } from "@/store/api/chatApi";
import { useGetMeQuery } from "@/store/api/authApi";
import { v4 as uuidv4 } from "uuid";

interface HITLApprovalProps {
  items: HITLRequestedItem[];
}

export default function HITLApproval({ items }: HITLApprovalProps) {
  const dispatch = useAppDispatch();
  const { sessionId, enabledAgentIds, enabledMcpToolIds } = useAppSelector(
    (state) => state.chat
  );
  const [sendMessage] = useSendMessageMutation();
  const { data: user } = useGetMeQuery();

  const buildMetadata = () => {
    const metadata: Record<string, unknown> = {};
    if (enabledAgentIds !== null) {
      metadata.enabled_agent_ids = enabledAgentIds;
    }
    if (enabledMcpToolIds !== null) {
      metadata.enabled_mcp_tool_ids = enabledMcpToolIds;
    }
    return Object.keys(metadata).length > 0 ? metadata : undefined;
  };

  const handleApproval = async (
    item: HITLRequestedItem,
    confirmed: boolean
  ) => {
    if (!user) return;

    const label = confirmed ? "Approved" : "Rejected";
    const userMsg: ChatMessage = {
      id: uuidv4(),
      role: "human",
      content: `${label}: ${item.function_name}`,
      timestamp: new Date().toISOString(),
    };
    dispatch(addMessage(userMsg));
    dispatch(setLoading(true));

    try {
      const metadata = buildMetadata();
      const response = await sendMessage({
        user_id: user.id,
        session_id: sessionId,
        content: {
          ...(metadata ? { metadata } : {}),
          hitl_approval: [
            {
              function_id: item.function_id,
              function_name: item.function_name,
              confirmed,
              payload: item.payload,
            },
          ],
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
      dispatch(
        addMessage({
          id: uuidv4(),
          role: "assistant",
          content: "Failed to process approval. Please try again.",
          timestamp: new Date().toISOString(),
        })
      );
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1, mt: 1 }}>
      {items.map((item) => (
        <Card
          key={item.function_id}
          sx={{ maxWidth: "75%", border: "1px solid rgba(255, 152, 0, 0.3)" }}
        >
          <CardContent sx={{ py: 1.5, px: 2, "&:last-child": { pb: 1.5 } }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                mb: 0.5,
              }}
            >
              <Chip
                label="Approval Required"
                size="small"
                color="warning"
                variant="outlined"
              />
              <Typography variant="body2" fontWeight={600}>
                {item.function_name}
              </Typography>
            </Box>
            {item.hint && (
              <Typography variant="caption" color="text.secondary">
                {item.hint}
              </Typography>
            )}
            {item.payload && Object.keys(item.payload).length > 0 && (
              <Box
                sx={{
                  mt: 1,
                  p: 1,
                  bgcolor: "rgba(255,255,255,0.03)",
                  borderRadius: 1,
                  fontSize: 12,
                  fontFamily: "monospace",
                  maxHeight: 120,
                  overflow: "auto",
                }}
              >
                <pre style={{ margin: 0 }}>
                  {JSON.stringify(item.payload, null, 2)}
                </pre>
              </Box>
            )}
            <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
              <Button
                size="small"
                variant="contained"
                color="success"
                onClick={() => handleApproval(item, true)}
              >
                Approve
              </Button>
              <Button
                size="small"
                variant="outlined"
                color="error"
                onClick={() => handleApproval(item, false)}
              >
                Reject
              </Button>
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
