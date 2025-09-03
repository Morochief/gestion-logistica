import React, { useEffect, lazy, Suspense } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import PrivateRoute from "./components/PrivateRoute";
import Layout from "./components/Layout";
import { initializeAuth } from "./utils/auth";

// Lazy loading de componentes
const Login = lazy(() => import("./pages/Login"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Usuarios = lazy(() => import("./pages/Usuarios"));
const Paises = lazy(() => import("./pages/Paises"));
const Ciudades = lazy(() => import("./pages/Ciudades"));
const Remitentes = lazy(() => import("./pages/Remitentes"));
const Transportadoras = lazy(() => import("./pages/Transportadoras"));
const Monedas = lazy(() => import("./pages/Monedas"));
const Honorarios = lazy(() => import("./pages/Honorarios"));
const CRT = lazy(() => import("./pages/CRT"));
const ListarCRT = lazy(() => import("./pages/ListarCRT"));
const MICNuevo = lazy(() => import("./pages/MICNuevo"));
const MICDetalle = lazy(() => import("./pages/MICDetalle"));
const MICsGuardados = lazy(() => import("./pages/MICsGuardados"));

// Componentes importados con lazy loading arriba

function App() {
  // Inicializar autenticación al cargar la aplicación
  useEffect(() => {
    initializeAuth();
  }, []);

  // Componente de loading
  const LoadingSpinner = () => (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Cargando...</p>
      </div>
    </div>
  );

  return (
    <ThemeProvider>
      <Router>
        <Suspense fallback={<LoadingSpinner />}>
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
          path="/crt/edit/:crtId"
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

        {/* MIC - flujo clásico que mantenés */}
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

        {/* 🔁 Reemplazo: ahora /mic usa MICsGuardados */}
        <Route
          path="/mic"
          element={
            <PrivateRoute>
              <Layout>
                <MICsGuardados />
              </Layout>
            </PrivateRoute>
          }
        />

        {/* También podés entrar por /mics o /mics-guardados */}
        <Route
          path="/mics"
          element={
            <PrivateRoute>
              <Layout>
                <MICsGuardados />
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
        </Suspense>
      </Router>
    </ThemeProvider>
  );
}

export default App;
