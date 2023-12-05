import React from 'react'
import TestGraph from '@/components/TestGraph'

const page = () => {
    const testId = 1
  return (
    <div className="bg-white mx-full max-w-full sm:px-10 lg:px-12">
      <div className="flex items-baseline justify-between border-b border-gray-200 pb-6 pt-24">
        <h1 className="text-4xl font-bold tracking-tight text-gray-700">Testing</h1>
      </div>
      <div className='mt-6'>
        <TestGraph 
        testIdIn = {testId}
        />
      </div>
    </div>
  )
}

export default page