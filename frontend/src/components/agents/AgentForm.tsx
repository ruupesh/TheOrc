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
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import type { Agent } from "@/lib/types";
import {
  useCreateAgentMutation,
  useUpdateAgentMutation,
} from "@/store/api/agentsApi";
import { useSnackbar } from "notistack";

const schema = z.object({
  name: z.string().min(1, "Required").max(255),
  description: z.string().min(1, "Required").max(2000),
  host: z.string().min(1, "Required").max(500),
  port: z.number().int().min(1).max(65535),
  agent_card_path: z.string().max(500).optional(),
  timeout: z.number().min(1).optional(),
  full_history: z.boolean().optional(),
  authentication_flag: z.boolean().optional(),
  allow_conversation_history: z.boolean().optional(),
});

type FormData = z.infer<typeof schema>;

interface AgentFormProps {
  open: boolean;
  agent?: Agent | null;
  onClose: () => void;
}

export default function AgentForm({ open, agent, onClose }: AgentFormProps) {
  const isEdit = !!agent;
  const { enqueueSnackbar } = useSnackbar();
  const [createAgent, { isLoading: isCreating }] = useCreateAgentMutation();
  const [updateAgent, { isLoading: isUpdating }] = useUpdateAgentMutation();
  const isLoading = isCreating || isUpdating;

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "",
      description: "",
      host: "http://localhost",
      port: 8001,
      agent_card_path: "/.well-known/agent.json",
      timeout: 300,
      full_history: true,
      authentication_flag: false,
      allow_conversation_history: true,
    },
  });

  useEffect(() => {
    if (agent) {
      reset({
        name: agent.name,
        description: agent.description,
        host: agent.host,
        port: agent.port,
        agent_card_path: agent.agent_card_path,
        timeout: agent.timeout,
        full_history: agent.full_history,
        authentication_flag: agent.authentication_flag,
        allow_conversation_history: agent.allow_conversation_history,
      });
    } else {
      reset({
        name: "",
        description: "",
        host: "http://localhost",
        port: 8001,
        agent_card_path: "/.well-known/agent.json",
        timeout: 300,
        full_history: true,
        authentication_flag: false,
        allow_conversation_history: true,
      });
    }
  }, [agent, reset]);

  const onSubmit = async (data: FormData) => {
    try {
      if (isEdit && agent) {
        await updateAgent({ id: agent.id, data }).unwrap();
        enqueueSnackbar("Agent updated", { variant: "success" });
      } else {
        await createAgent(data).unwrap();
        enqueueSnackbar("Agent created", { variant: "success" });
      }
      onClose();
    } catch {
      enqueueSnackbar("Operation failed", { variant: "error" });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEdit ? "Edit Agent" : "Add Agent"}</DialogTitle>
      <DialogContent>
        <Box
          component="form"
          id="agent-form"
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
            label="Description"
            fullWidth
            multiline
            rows={3}
            error={!!errors.description}
            helperText={errors.description?.message}
            {...register("description")}
          />
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField
              label="Host"
              fullWidth
              error={!!errors.host}
              helperText={errors.host?.message}
              {...register("host")}
            />
            <TextField
              label="Port"
              type="number"
              sx={{ width: 120 }}
              error={!!errors.port}
              helperText={errors.port?.message}
              {...register("port", { valueAsNumber: true })}
            />
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField
              label="Agent Card Path"
              fullWidth
              {...register("agent_card_path")}
            />
            <TextField
              label="Timeout (s)"
              type="number"
              sx={{ width: 120 }}
              {...register("timeout", { valueAsNumber: true })}
            />
          </Box>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            <Controller
              name="full_history"
              control={control}
              render={({ field }) => (
                <Box sx={{ display: "flex", flexDirection: "column", minWidth: 180 }}>
                  <FormControlLabel
                    control={<Switch checked={field.value} onChange={field.onChange} />}
                    label="Full History"
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                    Sends full prior context for stateless remote runs.
                  </Typography>
                </Box>
              )}
            />
            <Controller
              name="authentication_flag"
              control={control}
              render={({ field }) => (
                <Box sx={{ display: "flex", flexDirection: "column", minWidth: 180 }}>
                  <FormControlLabel
                    control={<Switch checked={field.value} onChange={field.onChange} />}
                    label="Auth Required"
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                    Adds bearer auth when calling this agent.
                  </Typography>
                </Box>
              )}
            />
            <Controller
              name="allow_conversation_history"
              control={control}
              render={({ field }) => (
                <Box sx={{ display: "flex", flexDirection: "column", minWidth: 180 }}>
                  <FormControlLabel
                    control={<Switch checked={field.value} onChange={field.onChange} />}
                    label="Allow History"
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                    Forwards conversation history in A2A metadata.
                  </Typography>
                </Box>
              )}
            />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          type="submit"
          form="agent-form"
          variant="contained"
          disabled={isLoading}
        >
          {isLoading ? <CircularProgress size={20} /> : isEdit ? "Save" : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
