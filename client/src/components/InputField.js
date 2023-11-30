import React from 'react';

const InputField = ({ label, id, name, placeholder, unit, onChange }) => {
  return (
    <>
      <label htmlFor={id} className="block text-sm mt-8 font-medium leading-6 text-gray-900">
        {label}
      </label>
      <div className="relative mt-2 rounded-md shadow-sm">
        {unit && (
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
            <span className="text-gray-500 sm:text-sm">{unit}</span>
          </div>
        )}
        <input
          type="text"
          name={name}
          id={id}
          className="block w-full rounded-md border-0 py-1.5 pl-3 pr-20 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
          placeholder={placeholder}
          style={{ paddingRight: unit ? '3rem' : undefined }}
          onChange={onChange}
        />
      </div>
    </>
  );
};

export default InputField;
