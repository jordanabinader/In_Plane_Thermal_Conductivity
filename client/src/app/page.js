import React from 'react';
import Procedure from '../components/Procedure';
import Hero from '../components/Hero';
import TestConstants from '../components/TestConstants';
import NavBar from '@/components/Nav';
import Footer from '@/components/Footer';
export default function Home() {

  return (
      <main>
        <NavBar/>
        <Hero />
        <Procedure />
        <TestConstants />
      </main>
  );
}
