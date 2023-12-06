'use client'
import React from 'react'
import { useRouter } from 'next/navigation'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

const RunningTest = (testData) => {
    const router = useRouter();

    const goToTest = () => {
      router.push(`/test/${testData.testData.testId}`);
    };

  return (
    <div className="fixed right-4 mt-20 z-10 bg-white rounded outline outline-red-400 sm:p-6 sm:pb-4">
      <div className="sm:flex sm:items-start">
        <div className="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
          <ExclamationTriangleIcon className="h-6 w-6 text-red-600" aria-hidden="true" />
        </div>
        <div className="mt-3 sm:ml-4 sm:mt-0 sm:text-left">
          <h3 className="text-base p-2 font-semibold leading-6 text-gray-900">
            Test: {testData.testData.testName} is running
          </h3>
          <div className="mt-2">
            <p className="text-sm mb-2 ml-2 text-gray-500">
                Material: {testData.testData.material}
            </p>
            <p className="text-sm mb-2 ml-2 text-gray-500">
                TC Distance: {testData.testData.tcDistance}
            </p>
          </div>
            <button 
                className="rounded-md bg-red-600 mt-3 px-3.5 py-2.5 mb-2 ml-2 mb-4 text-md font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600" 
                aria-current="page" 
                type="button" 
                onClick={goToTest}
            >
                Go to Test
            </button>
        </div>
      </div>
    </div>
  )
}

export default RunningTest
