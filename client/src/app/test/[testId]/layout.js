import React from "react";
import TestNav from '@/components/TestNav'
import Footer from "@/components/Footer";

export default function DashboardLayout({
    children, // will be a page or nested layout
  }) {
    return (
      <section>
        <TestNav/>
        {children}
      </section>
    )
  }