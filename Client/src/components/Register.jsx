import axios from "axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TextField, Box, Typography, Alert, Link } from "@mui/material";
import Button from "@mui/material/Button";
import login_bg from "../assets/home.png";

export default function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    username: "",
  });

  const [alertData, setAlertData] = useState({
    isOpened: false,
    severity: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const { email, password, username } = formData;
    const finalObj = { email, password, name: username };

    console.log(finalObj);
    try {
      const response = await axios.post(
        "http://localhost:8000/auth/register",
        finalObj
      );
      const { user } = response.data;
      setAlertData({
        isOpened: true,
        message: "Registered successfully!",
        severity: "success",
      });
    } catch (error) {
      setAlertData({
        isOpened: true,
        message: "Registration failed. Please try again.",
        severity: "error",
      });
    }
  };

  const handleRegisterNav = (e) => {
    e.preventDefault();
    navigate("/login");
  };
  return (
    <div className="flex flex-col items-center justify-center h-full bg-[#7cb4ec]">
      {alertData.isOpened && (
        <Alert className="absolute top-3" severity={alertData.severity}>
          {alertData.message}
        </Alert>
      )}
      <form
        onSubmit={(e) => handleLogin(e)}
        className="border-1  flex flex-col bg-white shadow  border-gray-300 rounded-2xl w-2/3 h-4/6"
      >
        <div className="flex h-full">
          <div className="w-1/2 h-full bg-blue-200 rounded-l-2xl">
            <img
              src={login_bg}
              alt=""
              className="h-full w-full object-cover rounded-l-2xl"
            />
          </div>
          <div className="w-1/2 p-4">
            <div className="h-full flex items-center justify-center">
              <Box
                sx={{
                  gap: 1,
                  display: "flex",
                  flexDirection: "column",
                  width: "60%",
                  height: "100%",
                  justifyContent: "center",
                }}
              >
                <Typography sx={{ marginBottom: 0 }} variant="h4" gutterBottom>
                  Register Now!
                </Typography>
                <Typography variant="body1" gutterBottom>
                  Please fill in the details to register
                </Typography>
                <TextField
                  label="Email"
                  variant="outlined"
                  size="small"
                  type="email"
                  name="email"
                  onChange={handleChange}
                  required
                />
                <TextField
                  label="Username"
                  variant="outlined"
                  size="small"
                  type="text"
                  name="username"
                  onChange={handleChange}
                  required
                />
                <TextField
                  label="Password"
                  variant="outlined"
                  size="small"
                  type="password"
                  name="password"
                  onChange={handleChange}
                  required
                />
                <TextField
                  label="Re-enter Password"
                  variant="outlined"
                  size="small"
                  type="password"
                  name="confirmPassword"
                  onChange={handleChange}
                  required
                />
                <Button type="submit" variant="contained">
                  Register
                </Button>

                <Box
                  sx={{
                    typography: "body1",
                    "& > :not(style) ~ :not(style)": {
                      ml: 2,
                    },
                  }}
                >
                  <Link
                    component="button" // 👈 renders a <button> instead of <a>
                    onClick={(e) => handleRegisterNav(e)}
                    underline="hover"
                  >
                    Already have an account? Login
                  </Link>
                </Box>
              </Box>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
