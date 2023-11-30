'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import InputField from './InputField';
import { My_Soul } from 'next/font/google';
import Modal from './Modal';
import axios from 'axios';

const TestConstants = () => {

  const router = useRouter();

  const [testSetup, setTestSetup] = useState({
    testName: '',
    material: '',
    density: '1',
    specificHeatCapacity: '1',
    tcDistance: '',
  });

  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setTestSetup(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (testSetup) => {

    try {
      let dataToSend;
      if (testSetup instanceof FormData) {
        dataToSend = Object.fromEntries(testSetup.entries());
      } else {
        dataToSend = testSetup; 
      }

      const response = await axios.post('http://localhost:80/startTest', testSetup);
    
      // Send request to controls and what's needed

      console.log('Test started successfully:', response.data);
      // Redirect to test of testId
      const testId = response.data.testId; 
      router.push(`/test/${testId}`);

    } catch (error) {
      console.error('Error starting test:', error);
      // Handle errors here (e.g., showing error messages to the user)
    }
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
  }

  const handleCloseModal = () => {
    setIsModalOpen(false);
  }

  return (
    <form className='bg-gray-100'>
      <div className="mx-auto grid max-w-2xl gap-x-8 gap-y-16 px-4 py-2 sm:px-6 sm:py-20 lg:max-w-7xl lg:grid-cols-2 lg:px-8">
        <div className='flex justify-center items-center'>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Test Set Up
          </h1>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:gap-6 lg:gap-2">
          <div className="border-l border-gray-300 px-14">
            <InputField
              label="Test Name"
              id="testname"
              name="testName"
              placeholder="Test #1"
              value={testSetup.testName}
              onChange={handleChange}
            />
            <InputField
              label="Material"
              id="material"
              name="material"
              placeholder="Copper"
              value={testSetup.material}
              onChange={handleChange}
            />
            <InputField
              label="Material Density"
              id="density"
              name="Density"
              placeholder="8.96"
              unit="g/cm3"
              value={testSetup.density}
              onChange={handleChange}
            />
            <InputField
              label="Specific Heat Capacity"
              id="cp"
              name="specificHeat"
              placeholder="0.385"
              unit="J/Kg.C"
              value={testSetup.specificHeat}
              onChange={handleChange}
            />
            <InputField
              label="Thermocouple Distance"
              id="tcdistance"
              name="tcdistance"
              placeholder="5"
              unit="mm"
              value={testSetup.tcdistance}
              onChange={handleChange}
            />
          </div>
          <div className="flex justify-center">
            <button 
              className="rounded-md bg-red-600 px-3.5 py-2.5 mt-8 text-md font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
              aria-current="page"
              type="button"
              onClick={handleOpenModal}
            >
              Start Test
            </button>
            {isModalOpen && (
                <Modal 
                  action="Start Test"
                  onCancel={handleCloseModal}
                  onSubmit={() => handleSubmit(testSetup)}
                />                
            )}
          </div>  
        </div>
      </div>
    </form>
  );
};

export default TestConstants;
