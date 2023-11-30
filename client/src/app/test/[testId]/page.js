'use client'
import React, { useState, useEffect } from 'react';
import TestGraph from '@/components/TestGraph';
import axios from 'axios';

async function queryRowsByTestId(tableName, testId) {
  try {
    const response = await axios.get(`http://localhost:80/queryRowsByTestId/${tableName}/${testId}`);
    console.log('Data retrieved successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

const TestPage = (props) => {
  const { testId } = props.params;
  const [testName, setTestName] = useState('');
  useEffect(() => {
    queryRowsByTestId('test_directory', testId)
      .then(data => {
        console.log('Fetched data:', data); 
        if (data && data.length > 0 && data[0].testName) {
          setTestName(data[0].testName);
        } else {
          setTestName('Test name not found');
        }
      })
      .catch(error => {
        console.error('Error in fetching test name:', error);
      });
  }, [testId]);

  return (
    <div className="bg-white mx-full max-w-full sm:px-10 lg:px-12">
      <div className="flex items-baseline justify-between border-b border-gray-200 pb-6 pt-24">
        <h1 className="text-4xl font-bold tracking-tight text-gray-700">{testName || 'Loading...'}</h1>
      </div>
      <div className='mt-6'>
        <TestGraph 
        testIdIn = {testId}
        />
      </div>
    </div>
  );
};

export default TestPage;
