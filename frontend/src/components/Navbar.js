import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { logout, getUser, isLoggedIn } from "../utils/auth";
import {
  FaHome,
  FaUser,
  FaGlobe,
  FaCity,
  FaTruck,
  FaDollarSign,
  FaMoneyCheckAlt,
  FaFileAlt,
  FaFilePdf,
  FaSignOutAlt,
  FaBars,
  FaTimes,
  FaChevronDown,
  FaUserCircle,
} from "react-icons/fa";
import ThemeToggle from "./ThemeToggle";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  useEffect(() => {
    if (isLoggedIn()) {
      const userData = getUser();
      setUser(userData);
    }
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const toggleUserMenu = () => {
    setIsUserMenuOpen(!isUserMenuOpen);
  };

  const closeMenus = () => {
    setIsMenuOpen(false);
    setIsUserMenuOpen(false);
  };

  const activeClass = (path) =>
    location.pathname.startsWith(path)
      ? "bg-indigo-900 text-white"
      : "text-indigo-100 hover:bg-indigo-700 hover:text-white";

  const navItems = [
    { path: "/", label: "Dashboard", icon: FaHome },
    { path: "/usuarios", label: "Usuarios", icon: FaUser },
    { path: "/paises", label: "Países", icon: FaGlobe },
    { path: "/ciudades", label: "Ciudades", icon: FaCity },
    { path: "/remitentes", label: "Remitentes", icon: FaUser },
    { path: "/transportadoras", label: "Transportadoras", icon: FaTruck },
    { path: "/crt", label: "CRT", icon: FaFilePdf, highlight: true },
    { path: "/monedas", label: "Monedas", icon: FaDollarSign },
    { path: "/honorarios", label: "Honorarios", icon: FaMoneyCheckAlt },
    { path: "/mics-guardados", label: "MICs Guardados", icon: FaFileAlt },
  ];

  if (!isLoggedIn()) return null;

  return (
    <nav className="bg-indigo-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo y título */}
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <div className="bg-white rounded-full p-2 mr-3">
                <FaFilePdf className="h-6 w-6 text-indigo-600" />
              </div>
              <div className="text-white font-bold text-lg">
                Sistema Logístico
              </div>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.slice(0, 8).map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition-colors duration-200 ${
                  item.highlight
                    ? "bg-yellow-500 text-indigo-900 hover:bg-yellow-400"
                    : activeClass(item.path)
                }`}
                onClick={closeMenus}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Theme Toggle */}
            <ThemeToggle />

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={toggleUserMenu}
                className="flex items-center text-white hover:text-gray-200 focus:outline-none focus:text-gray-200"
              >
                <FaUserCircle className="h-8 w-8 mr-2" />
                <span className="text-sm font-medium">
                  {user?.nombre_completo || user?.usuario || "Usuario"}
                </span>
                <FaChevronDown className="h-4 w-4 ml-1" />
              </button>
            </div>

            {isUserMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                <div className="px-4 py-2 text-sm text-gray-700 border-b">
                  <div className="font-medium">{user?.nombre_completo}</div>
                  <div className="text-gray-500">{user?.usuario}</div>
                  <div className="text-xs text-indigo-600 capitalize">
                    {user?.rol}
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                >
                  <FaSignOutAlt className="h-4 w-4" />
                  Cerrar Sesión
                </button>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={toggleMenu}
              className="text-white hover:text-gray-200 focus:outline-none focus:text-gray-200"
            >
              {isMenuOpen ? (
                <FaTimes className="h-6 w-6" />
              ) : (
                <FaBars className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 bg-indigo-900">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`block px-3 py-2 rounded-md text-base font-medium flex items-center gap-2 transition-colors duration-200 ${
                  item.highlight
                    ? "bg-yellow-500 text-indigo-900"
                    : activeClass(item.path)
                }`}
                onClick={closeMenus}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}

            {/* Mobile User Info */}
            <div className="border-t border-indigo-700 pt-4 mt-4">
              <div className="px-3 py-2">
                <div className="flex items-center">
                  <FaUserCircle className="h-8 w-8 text-white mr-3" />
                  <div>
                    <div className="text-white font-medium text-sm">
                      {user?.nombre_completo}
                    </div>
                    <div className="text-indigo-200 text-xs">
                      {user?.usuario}
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="mt-3 w-full flex items-center justify-center px-3 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors duration-200"
                >
                  <FaSignOutAlt className="h-4 w-4 mr-2" />
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Overlay for mobile menu */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          onClick={closeMenus}
        />
      )}
    </nav>
  );
}

export default Navbar;
