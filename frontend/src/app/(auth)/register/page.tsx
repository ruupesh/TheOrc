"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { useRegisterMutation } from "@/store/api/authApi";
import { useSnackbar } from "notistack";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Link from "next/link";
import CircularProgress from "@mui/material/CircularProgress";

const schema = z
  .object({
    email: z.string().email("Invalid email"),
    username: z.string().min(3, "Min 3 characters").max(100),
    password: z.string().min(8, "Min 8 characters").max(128),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const router = useRouter();
  const { enqueueSnackbar } = useSnackbar();
  const [registerUser, { isLoading }] = useRegisterMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      await registerUser({
        email: data.email,
        username: data.username,
        password: data.password,
      }).unwrap();
      enqueueSnackbar("Account created! Please sign in.", {
        variant: "success",
      });
      router.replace("/login");
    } catch {
      enqueueSnackbar("Registration failed. Email or username may be taken.", {
        variant: "error",
      });
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
          Create a new account
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
            label="Username"
            fullWidth
            error={!!errors.username}
            helperText={errors.username?.message}
            {...register("username")}
          />
          <TextField
            label="Password"
            type="password"
            fullWidth
            error={!!errors.password}
            helperText={errors.password?.message}
            {...register("password")}
          />
          <TextField
            label="Confirm Password"
            type="password"
            fullWidth
            error={!!errors.confirmPassword}
            helperText={errors.confirmPassword?.message}
            {...register("confirmPassword")}
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={isLoading}
            sx={{ mt: 1, py: 1.2 }}
          >
            {isLoading ? <CircularProgress size={22} /> : "Create Account"}
          </Button>
          <Typography variant="body2" sx={{ textAlign: "center", mt: 1 }}>
            Already have an account?{" "}
            <Link
              href="/login"
              style={{ color: "#7c4dff", textDecoration: "none" }}
            >
              Sign In
            </Link>
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
