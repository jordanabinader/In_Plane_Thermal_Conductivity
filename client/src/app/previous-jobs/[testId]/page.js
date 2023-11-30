import React from 'react';

export default function EditPreviousJob(props) {
  const { testId } = props.params;
  const testToLoad = "http://localhost:8124/" + testId.toString();

  return (
    <div className="bg-white mx-full max-w-full sm:px-10 lg:px-12">
      <div className="flex items-baseline justify-between border-b border-gray-200 pt-24">
        <h1 className="text-4xl font-bold tracking-tight text-gray-700">Test</h1>
      </div>
      <div className='mt-6'>
        <div className='bg-white'>
          <iframe
            title="Bokeh Plot"
            //src="http://localhost:8124/1"
            src={testToLoad}
            width="100%"
            height="650"
            style={{ border: 'none' }}
          />
        </div>
      </div>
    </div>    
  );
}