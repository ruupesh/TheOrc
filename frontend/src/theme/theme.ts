"use client";

import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#7c4dff",
      light: "#b47cff",
      dark: "#3f1dcb",
    },
    secondary: {
      main: "#00e5ff",
      light: "#6effff",
      dark: "#00b2cc",
    },
    background: {
      default: "#0a0a0a",
      paper: "#141414",
    },
    divider: "rgba(255,255,255,0.08)",
    text: {
      primary: "#ededed",
      secondary: "#a0a0a0",
    },
  },
  typography: {
    fontFamily: "var(--font-geist-sans), Arial, sans-serif",
    h4: { fontWeight: 700 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  shape: {
    borderRadius: 10,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: "1px solid rgba(255,255,255,0.08)",
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundImage: "none",
          border: "1px solid rgba(255,255,255,0.08)",
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: "1px solid rgba(255,255,255,0.08)",
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: "outlined",
        size: "small",
      },
    },
  },
});

export default theme;
