"use client";

import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "@/lib/auth";
import { useGetMeQuery } from "@/store/api/authApi";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import ChatIcon from "@mui/icons-material/ChatBubbleOutline";
import AgentIcon from "@mui/icons-material/SmartToyOutlined";
import ToolIcon from "@mui/icons-material/BuildOutlined";
import StoreIcon from "@mui/icons-material/StorefrontOutlined";
import LogoutIcon from "@mui/icons-material/LogoutOutlined";
import Avatar from "@mui/material/Avatar";

const DRAWER_WIDTH = 240;

const navItems = [
  { label: "Chat", href: "/chat", icon: <ChatIcon /> },
  { label: "Agents", href: "/agents", icon: <AgentIcon /> },
  { label: "MCP Tools", href: "/mcp-tools", icon: <ToolIcon /> },
  { label: "Marketplace", href: "/marketplace", icon: <StoreIcon /> },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { data: user } = useGetMeQuery();

  const handleLogout = () => {
    clearToken();
    router.replace("/login");
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
          bgcolor: "background.paper",
          display: "flex",
          flexDirection: "column",
        },
      }}
    >
      {/* Logo */}
      <Box sx={{ p: 2, display: "flex", alignItems: "center", gap: 1 }}>
        <Box
          sx={{
            width: 32,
            height: 32,
            borderRadius: 1,
            bgcolor: "primary.main",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: 16,
            color: "white",
          }}
        >
          O
        </Box>
        <Typography variant="h6" sx={{ fontSize: 16 }}>
          TheOrchestrator
        </Typography>
      </Box>

      <Divider />

      {/* Nav */}
      <List sx={{ flex: 1, px: 1, pt: 1 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={item.href}
            selected={pathname === item.href}
            onClick={() => router.push(item.href)}
            sx={{
              borderRadius: 1,
              mb: 0.5,
              "&.Mui-selected": {
                bgcolor: "rgba(124, 77, 255, 0.12)",
                "&:hover": {
                  bgcolor: "rgba(124, 77, 255, 0.18)",
                },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.label}
              primaryTypographyProps={{ fontSize: 14 }}
            />
          </ListItemButton>
        ))}
      </List>

      <Divider />

      {/* User */}
      <Box
        sx={{
          p: 2,
          display: "flex",
          alignItems: "center",
          gap: 1,
        }}
      >
        <Avatar sx={{ width: 32, height: 32, bgcolor: "primary.dark", fontSize: 14 }}>
          {user?.username?.[0]?.toUpperCase() || "U"}
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="body2" noWrap>
            {user?.username || "User"}
          </Typography>
          <Typography variant="caption" color="text.secondary" noWrap>
            {user?.email || ""}
          </Typography>
        </Box>
        <IconButton size="small" onClick={handleLogout} title="Logout">
          <LogoutIcon fontSize="small" />
        </IconButton>
      </Box>
    </Drawer>
  );
}
