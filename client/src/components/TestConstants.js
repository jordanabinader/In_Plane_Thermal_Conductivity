'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import InputField from './InputField';
import { My_Soul } from 'next/font/google';
import Modal from './Modal';
import axios from 'axios';
import Loader from './Loader'

const TestConstants = () => {

  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isCompliant, setIsCompliant] = useState(true)
  const [testSetup, setTestSetup] = useState({
    testName: '',
    material: '',
    density: '1',
    specificHeatCapacity: '1',
    tcDistance: 0,
  });

  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updatedValue = name === 'tcDistance' ? Number(value) : value;
    setTestSetup(prevState => ({
      ...prevState,
      [name]: updatedValue
    }));
  };

  const handleSubmit = async (testSetup) => {

    let testId;
    let errorMessageIn = '';

    try {
      let dataToSend;
      if (testSetup instanceof FormData) {
        dataToSend = Object.fromEntries(testSetup.entries());
      } else {
        dataToSend = testSetup; 
      }

      const response = await axios.post('http://localhost:2999/startTest', testSetup);
      console.log('Test started successfully:', response.data);
      testId = response.data.testId; 
      setIsCompliant(true);
      } catch (error) {
        console.error('Error starting test:', error);
        errorMessageIn = 'Error starting test: ' + error.response.data; 
        setIsModalOpen(false);
        setIsCompliant(false);
        setErrorMessage(errorMessage); // Display the error message in UI
        return;
      } 

    try {

      setIsLoading(true);

      const responseStart = await axios.put('http://localhost:3001/test-start'); //returns 200 if picotalker is up and 404 if picotalker not up or Json one key is live, error, timeout, connection refused
      
      if (responseStart.status === 200) {
        setIsLoading(false);
        router.push(`/test/${testId}`);
      } else {
        console.error('Error starting controls: Unexpected response status', responseStart);
      }

    } catch (error) {

      console.error('Error starting controls:', error)
      setIsLoading(false)
      setIsModalOpen(false)

    } 
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
  }

  const handleCloseModal = () => {
    setIsModalOpen(false);
  }

  if (isLoading) {
    return <Loader />
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
            {!isCompliant && (
              <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <strong class="font-bold">Wrong Inputs!</strong>
                <span class="block sm:inline">{errorMessage}</span>
                <span class="absolute top-0 bottom-0 right-0 px-4 py-3">
                  <svg class="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/></svg>
                </span>
            </div>
            )}
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
              name="density"
              placeholder="8.96"
              unit="g/cm3"
              value={testSetup.density}
              onChange={handleChange}
            />
            <InputField
              label="Specific Heat Capacity"
              id="cp"
              name="specificHeatCapacity"
              placeholder="0.385"
              unit="J/Kg.C"
              value={testSetup.specificHeatCapacity}
              onChange={handleChange}
            />
            <InputField
              label="Thermocouple Distance"
              id="tcdistance"
              name="tcDistance"
              placeholder="5"
              unit="mm"
              value={testSetup.tcDistance}
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
