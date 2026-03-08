"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { useLoginMutation } from "@/store/api/authApi";
import { setToken } from "@/lib/auth";
import { useSnackbar } from "notistack";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Link from "next/link";
import CircularProgress from "@mui/material/CircularProgress";

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(1, "Password is required"),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const { enqueueSnackbar } = useSnackbar();
  const [login, { isLoading }] = useLoginMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      const result = await login(data).unwrap();
      setToken(result.access_token);
      router.replace("/chat");
    } catch {
      enqueueSnackbar("Invalid email or password", { variant: "error" });
    }
  };

  return (
    <Card sx={{ width: "100%", maxWidth: 420, mx: 2 }}>
      <CardContent sx={{ p: 4 }}>
        <Typography variant="h5" sx={{ mb: 1, textAlign: "center" }}>
          TheOrchestrator
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 3, textAlign: "center" }}
        >
          Sign in to your account
        </Typography>
        <Box
          component="form"
          onSubmit={handleSubmit(onSubmit)}
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <TextField
            label="Email"
            type="email"
            fullWidth
            error={!!errors.email}
            helperText={errors.email?.message}
            {...register("email")}
          />
          <TextField
            label="Password"
            type="password"
            fullWidth
            error={!!errors.password}
            helperText={errors.password?.message}
            {...register("password")}
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={isLoading}
            sx={{ mt: 1, py: 1.2 }}
          >
            {isLoading ? <CircularProgress size={22} /> : "Sign In"}
          </Button>
          <Typography variant="body2" sx={{ textAlign: "center", mt: 1 }}>
            Don&apos;t have an account?{" "}
            <Link
              href="/register"
              style={{ color: "#7c4dff", textDecoration: "none" }}
            >
              Sign Up
            </Link>
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
