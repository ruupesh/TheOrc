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
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Typography from "@mui/material/Typography";
import { useGetAgentsQuery } from "@/store/api/agentsApi";
import { useGetMcpToolsQuery } from "@/store/api/mcpToolsApi";
import { useGetMeQuery } from "@/store/api/authApi";
import { usePublishItemMutation } from "@/store/api/marketplaceApi";
import { useSnackbar } from "notistack";

const schema = z.object({
  item_type: z.enum(["agent", "mcp_tool"]),
  item_id: z.string().min(1, "Select an item"),
  title: z.string().min(1, "Required").max(500),
  description: z.string().min(1, "Required").max(5000),
  visibility: z.enum(["public", "private"]),
});

type FormData = z.infer<typeof schema>;

interface PublishDialogProps {
  open: boolean;
  onClose: () => void;
}

export default function PublishDialog({ open, onClose }: PublishDialogProps) {
  const { enqueueSnackbar } = useSnackbar();
  const { data: agents } = useGetAgentsQuery();
  const { data: mcpTools } = useGetMcpToolsQuery();
  const { data: user } = useGetMeQuery();
  const [publishItem, { isLoading }] = usePublishItemMutation();
  const currentUserId = user?.id ? String(user.id) : "";

  const {
    register,
    handleSubmit,
    reset,
    watch,
    control,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      item_type: "agent",
      item_id: "",
      title: "",
      description: "",
      visibility: "public",
    },
  });

  const itemType = watch("item_type");

  useEffect(() => {
    if (!open) reset();
  }, [open, reset]);

  // Reset item selection when type changes
  useEffect(() => {
    setValue("item_id", "");
  }, [itemType, setValue]);

  const myAgents =
    agents?.filter(
      (a) => !a.is_system && !!currentUserId && String(a.owner_id) === currentUserId
    ) || [];
  const myTools =
    mcpTools?.filter(
      (t) => !t.is_system && !!currentUserId && String(t.owner_id) === currentUserId
    ) || [];
  const items = itemType === "agent" ? myAgents : myTools;

  const onSubmit = async (data: FormData) => {
    try {
      await publishItem({
        agent_id: data.item_type === "agent" ? data.item_id : undefined,
        mcp_tool_id: data.item_type === "mcp_tool" ? data.item_id : undefined,
        title: data.title,
        description: data.description,
        visibility: data.visibility,
      }).unwrap();
      enqueueSnackbar("Published to marketplace", { variant: "success" });
      onClose();
    } catch {
      enqueueSnackbar("Failed to publish", { variant: "error" });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Publish to Marketplace</DialogTitle>
      <DialogContent>
        <Box
          component="form"
          id="publish-form"
          onSubmit={handleSubmit(onSubmit)}
          sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}
        >
          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: "block" }}>
              Type
            </Typography>
            <Controller
              name="item_type"
              control={control}
              render={({ field }) => (
                <ToggleButtonGroup
                  value={field.value}
                  exclusive
                  onChange={(_, val) => val && field.onChange(val)}
                  fullWidth
                  size="small"
                >
                  <ToggleButton value="agent">Agent</ToggleButton>
                  <ToggleButton value="mcp_tool">MCP Tool</ToggleButton>
                </ToggleButtonGroup>
              )}
            />
          </Box>

          <TextField
            label={itemType === "agent" ? "Agent" : "MCP Tool"}
            select
            fullWidth
            defaultValue=""
            error={!!errors.item_id}
            helperText={errors.item_id?.message}
            {...register("item_id")}
          >
            {items.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            label="Title"
            fullWidth
            error={!!errors.title}
            helperText={errors.title?.message}
            {...register("title")}
          />
          <TextField
            label="Description"
            fullWidth
            multiline
            rows={4}
            error={!!errors.description}
            helperText={errors.description?.message}
            {...register("description")}
          />

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: "block" }}>
              Visibility
            </Typography>
            <Controller
              name="visibility"
              control={control}
              render={({ field }) => (
                <ToggleButtonGroup
                  value={field.value}
                  exclusive
                  onChange={(_, val) => val && field.onChange(val)}
                  fullWidth
                  size="small"
                >
                  <ToggleButton value="public">Public</ToggleButton>
                  <ToggleButton value="private">Private</ToggleButton>
                </ToggleButtonGroup>
              )}
            />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          type="submit"
          form="publish-form"
          variant="contained"
          disabled={isLoading}
        >
          {isLoading ? <CircularProgress size={20} /> : "Publish"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
