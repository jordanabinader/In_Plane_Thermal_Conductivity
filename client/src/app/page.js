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
  const [testData, setTestData] = useState(null);

  const getTableLastRow = async (tableName) => {
    try {
      const response = await axios.get(`http://localhost:2999/queryLastRow/${tableName}`);
      console.log('Success looking for active tests:', response.data.active)
      setTestData(response.data); // Store the entire response data in state
    } catch (error) {
      console.error("Error fetching the last row:", error.message);
    }
  }

  useEffect(() => {
    getTableLastRow('test_directory');
  }, []);

  return (
    <main>
      <NavBar />
      {testData && testData.active === 1 && (
        <RunningTest testData={testData} />
      )}
      <Hero />
      <Procedure />
      <TestConstants />
    </main>
  );
}
