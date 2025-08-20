import React, { useState } from "react";
import api from "../api/api";
import { login as loginAuth } from "../utils/auth";
import { useNavigate } from "react-router-dom";

function Login() {
  const [usuario, setUsuario] = useState("");
  const [clave, setClave] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/auth/login", { usuario, clave });
      loginAuth(res.data.token);
      navigate("/");
    } catch (err) {
      setError("Usuario o clave incorrectos");
    }
  };

  return (
    <div className="login-container">
      <h2>Iniciar sesión</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Usuario"
          value={usuario}
          onChange={(e) => setUsuario(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Clave"
          value={clave}
          onChange={(e) => setClave(e.target.value)}
          required
        />
        <button type="submit">Ingresar</button>
        {error && <div style={{ color: "red", marginTop: "8px" }}>{error}</div>}
      </form>
    </div>
  );
}

export default Login;
