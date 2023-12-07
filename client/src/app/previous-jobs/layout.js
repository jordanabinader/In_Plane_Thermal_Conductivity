import React from "react";
import NavBar from "@/components/Nav";
import Footer from "@/components/Footer";
import RunningTest from "@/components/RunningTest";

export default function DashboardLayout({
    children, // will be a page or nested layout
  }) {
    return (
      <section>
        <NavBar/>
        <RunningTest/>
        {children}
      </section>
    )
  }