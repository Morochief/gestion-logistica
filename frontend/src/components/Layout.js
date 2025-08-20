import React from "react";
import CRTMenu from "./CRTMenu";
import Navbar from "./Navbar";

const Layout = ({ children }) => (
  <div className="flex min-h-screen">
    <aside className="group w-20 hover:w-40 transition-all duration-300 bg-gradient-to-b from-blue-100 to-blue-300 shadow-lg flex items-start pt-4">
      <CRTMenu />
    </aside>
    <div className="flex-1 flex flex-col">
      <Navbar />
      <main className="flex-1 bg-slate-50 p-6">{children}</main>
    </div>
  </div>
);

export default Layout;
