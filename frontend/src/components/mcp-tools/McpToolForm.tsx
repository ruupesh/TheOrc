"use client";

import { useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import type { McpTool } from "@/lib/types";
import {
  useCreateMcpToolMutation,
  useUpdateMcpToolMutation,
} from "@/store/api/mcpToolsApi";
import { useSnackbar } from "notistack";

const schema = z.object({
  name: z.string().min(1, "Required").max(255),
  connection_type: z.enum(["stdio", "streamable_http", "sse"]),
  command: z.string().max(255).optional(),
  args_text: z.string().optional(),
  env_text: z.string().optional(),
  url: z.string().max(1000).optional(),
  headers_text: z.string().optional(),
  sse_read_timeout: z.number().min(1).optional(),
  timeout: z.number().min(1).optional(),
  authentication_flag: z.boolean().optional(),
  auth_token: z.string().optional(),
  tool_filter_text: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface McpToolFormProps {
  open: boolean;
  tool?: McpTool | null;
  onClose: () => void;
}

function parseJsonSafe<T>(text: string | undefined, fallback: T | undefined): T | undefined {
  if (!text || !text.trim()) return fallback;
  try {
    return JSON.parse(text) as T;
  } catch {
    return fallback;
  }
}

export default function McpToolForm({ open, tool, onClose }: McpToolFormProps) {
  const isEdit = !!tool;
  const { enqueueSnackbar } = useSnackbar();
  const [createTool, { isLoading: isCreating }] = useCreateMcpToolMutation();
  const [updateTool, { isLoading: isUpdating }] = useUpdateMcpToolMutation();
  const isLoading = isCreating || isUpdating;

  const {
    register,
    handleSubmit,
    reset,
    watch,
    control,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "",
      connection_type: "stdio",
      command: "",
      args_text: "",
      env_text: "",
      url: "",
      headers_text: "",
      sse_read_timeout: 300,
      timeout: 30,
      authentication_flag: false,
      auth_token: "",
      tool_filter_text: "",
    },
  });

  const connectionType = watch("connection_type");

  useEffect(() => {
    if (tool) {
      reset({
        name: tool.name,
        connection_type: tool.connection_type as "stdio" | "streamable_http" | "sse",
        command: tool.command || "",
        args_text: tool.args ? JSON.stringify(tool.args, null, 2) : "",
        env_text: tool.env ? JSON.stringify(tool.env, null, 2) : "",
        url: tool.url || "",
        headers_text: tool.headers ? JSON.stringify(tool.headers, null, 2) : "",
        sse_read_timeout: tool.sse_read_timeout,
        timeout: tool.timeout,
        authentication_flag: tool.authentication_flag,
        auth_token: "",
        tool_filter_text: tool.tool_filter ? JSON.stringify(tool.tool_filter) : "",
      });
    } else {
      reset({
        name: "",
        connection_type: "stdio",
        command: "",
        args_text: "",
        env_text: "",
        url: "",
        headers_text: "",
        sse_read_timeout: 300,
        timeout: 30,
        authentication_flag: false,
        auth_token: "",
        tool_filter_text: "",
      });
    }
  }, [tool, reset]);

  const onSubmit = async (data: FormData) => {
    const payload = {
      name: data.name,
      connection_type: data.connection_type,
      command: data.command || undefined,
      args: parseJsonSafe<string[]>(data.args_text, undefined),
      env: parseJsonSafe<Record<string, string>>(data.env_text, undefined),
      url: data.url || undefined,
      headers: parseJsonSafe<Record<string, string>>(data.headers_text, undefined),
      sse_read_timeout: data.sse_read_timeout,
      timeout: data.timeout,
      authentication_flag: data.authentication_flag,
      auth_token: data.auth_token || undefined,
      tool_filter: parseJsonSafe<string[]>(data.tool_filter_text, undefined),
    };

    try {
      if (isEdit && tool) {
        await updateTool({ id: tool.id, data: payload }).unwrap();
        enqueueSnackbar("MCP tool updated", { variant: "success" });
      } else {
        await createTool(payload).unwrap();
        enqueueSnackbar("MCP tool created", { variant: "success" });
      }
      onClose();
    } catch {
      enqueueSnackbar("Operation failed", { variant: "error" });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEdit ? "Edit MCP Tool" : "Add MCP Tool"}</DialogTitle>
      <DialogContent>
        <Box
          component="form"
          id="mcp-tool-form"
          onSubmit={handleSubmit(onSubmit)}
          sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}
        >
          <TextField
            label="Name"
            fullWidth
            error={!!errors.name}
            helperText={errors.name?.message}
            {...register("name")}
          />
          <TextField
            label="Connection Type"
            select
            fullWidth
            defaultValue={tool?.connection_type || "stdio"}
            error={!!errors.connection_type}
            {...register("connection_type")}
          >
            <MenuItem value="stdio">stdio</MenuItem>
            <MenuItem value="streamable_http">streamable_http</MenuItem>
            <MenuItem value="sse">sse</MenuItem>
          </TextField>

          {connectionType === "stdio" ? (
            <>
              <TextField
                label="Command"
                fullWidth
                {...register("command")}
                placeholder="e.g. npx -y @mcp/server"
              />
              <TextField
                label="Args (JSON array)"
                fullWidth
                multiline
                rows={2}
                {...register("args_text")}
                placeholder='["--arg1", "--arg2"]'
              />
            </>
          ) : (
            <TextField
              label="URL"
              fullWidth
              {...register("url")}
              placeholder="https://example.com/mcp"
            />
          )}

          <TextField
            label="Environment Variables (JSON)"
            fullWidth
            multiline
            rows={2}
            {...register("env_text")}
            placeholder='{"KEY": "value"}'
          />

          {connectionType !== "stdio" && (
            <TextField
              label="Headers (JSON)"
              fullWidth
              multiline
              rows={2}
              {...register("headers_text")}
              placeholder='{"Authorization": "Bearer ..."}'
            />
          )}

          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField
              label="Timeout (s)"
              type="number"
              sx={{ flex: 1 }}
              {...register("timeout", { valueAsNumber: true })}
            />
            <TextField
              label="SSE Read Timeout (s)"
              type="number"
              sx={{ flex: 1 }}
              {...register("sse_read_timeout", { valueAsNumber: true })}
            />
          </Box>

          <Controller
            name="authentication_flag"
            control={control}
            render={({ field }) => (
              <FormControlLabel
                control={<Switch checked={field.value} onChange={field.onChange} />}
                label="Authentication Required"
              />
            )}
          />

          <TextField
            label="Auth Token"
            fullWidth
            type="password"
            {...register("auth_token")}
            placeholder="Leave empty to keep existing"
          />

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5 }}>
              Tool Filter (JSON array of tool names to include)
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={2}
              {...register("tool_filter_text")}
              placeholder='["tool_name_1", "tool_name_2"]'
            />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          type="submit"
          form="mcp-tool-form"
          variant="contained"
          disabled={isLoading}
        >
          {isLoading ? <CircularProgress size={20} /> : isEdit ? "Save" : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
