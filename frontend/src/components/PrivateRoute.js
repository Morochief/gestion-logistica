import { Navigate, useLocation } from "react-router-dom";
import { isLoggedIn } from "../utils/auth";

function PrivateRoute({ children }) {
  const location = useLocation();

  // Verificar si el usuario está autenticado
  if (!isLoggedIn()) {
    // Redirigir al login, guardando la ubicación actual para redirigir después
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

export default PrivateRoute;
