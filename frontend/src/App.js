import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Usuarios from "./pages/Usuarios";
import Paises from "./pages/Paises";
import Ciudades from "./pages/Ciudades";
import Remitentes from "./pages/Remitentes";
import Transportadoras from "./pages/Transportadoras";
import Monedas from "./pages/Monedas";
import Honorarios from "./pages/Honorarios";
import Movimientos from "./pages/Movimientos";
import Reportes from "./pages/Reportes";
import Parametros from "./pages/Parametros";
import CRT from "./pages/CRT";
import ListarCRT from "./pages/ListarCRT";

import MICNuevo from "./pages/MICNuevo"; // <- crea este archivo
import MICDetalle from "./pages/MICDetalle"; // <- crea este archivo
import ListarMIC from "./pages/ListarMIC"; // <- crea este archivo
import MICsGuardados from "./pages/MICsGuardados";

import PrivateRoute from "./components/PrivateRoute";
import Layout from "./components/Layout";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/usuarios"
          element={
            <PrivateRoute>
              <Layout>
                <Usuarios />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/paises"
          element={
            <PrivateRoute>
              <Layout>
                <Paises />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/ciudades"
          element={
            <PrivateRoute>
              <Layout>
                <Ciudades />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/remitentes"
          element={
            <PrivateRoute>
              <Layout>
                <Remitentes />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/transportadoras"
          element={
            <PrivateRoute>
              <Layout>
                <Transportadoras />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/monedas"
          element={
            <PrivateRoute>
              <Layout>
                <Monedas />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/honorarios"
          element={
            <PrivateRoute>
              <Layout>
                <Honorarios />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/movimientos"
          element={
            <PrivateRoute>
              <Layout>
                <Movimientos />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/reportes"
          element={
            <PrivateRoute>
              <Layout>
                <Reportes />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/parametros"
          element={
            <PrivateRoute>
              <Layout>
                <Parametros />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/crt"
          element={
            <PrivateRoute>
              <Layout>
                <CRT />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/listar-crt"
          element={
            <PrivateRoute>
              <Layout>
                <ListarCRT />
              </Layout>
            </PrivateRoute>
          }
        />

        {/* MIC - FLUJO COMPLETO */}
        <Route
          path="/mic/nuevo"
          element={
            <PrivateRoute>
              <Layout>
                <MICNuevo />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/mic/:id"
          element={
            <PrivateRoute>
              <Layout>
                <MICDetalle />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/mic"
          element={
            <PrivateRoute>
              <Layout>
                <ListarMIC />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/mics-guardados"
          element={
            <PrivateRoute>
              <Layout>
                <MICsGuardados />
              </Layout>
            </PrivateRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
