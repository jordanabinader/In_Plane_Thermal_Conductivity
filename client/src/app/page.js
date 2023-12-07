'use client'
import React, { useEffect, useState } from 'react';
import Procedure from '../components/Procedure';
import Hero from '../components/Hero';
import TestConstants from '../components/TestConstants';
import NavBar from '@/components/Nav';
import Footer from '@/components/Footer';
import axios from 'axios';
import RunningTest from '@/components/RunningTest';

export default function Home() {

  return (
    <main>
      <NavBar />
      <RunningTest/>
      <Hero />
      <Procedure />
      <TestConstants />
    </main>
  );
}
