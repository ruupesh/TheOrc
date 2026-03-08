"use client";

import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Provider as ReduxProvider } from "react-redux";
import { SnackbarProvider } from "notistack";
import { store } from "@/store/store";
import theme from "@/theme/theme";

export default function AppProviders({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ReduxProvider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider
          maxSnack={3}
          autoHideDuration={4000}
          anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        >
          {children}
        </SnackbarProvider>
      </ThemeProvider>
    </ReduxProvider>
  );
}
