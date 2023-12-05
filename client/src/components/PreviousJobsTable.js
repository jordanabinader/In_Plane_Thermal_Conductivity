'use client';
import React, {useState, useEffect} from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/20/solid';
import Modal from './Modal';

const itemsPerPage = 6;

const TableComponent = ({ data, handleDelete}) => {

  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Compute filtered data based on search term
  const filteredData = data.filter(item => 
    item.testName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const goToPage = (page, event) => {
    event.preventDefault();
    setCurrentPage(page);
  };

  const goToPreviousPage = (event) => {
    setCurrentPage((prevCurrentPage) => Math.max(prevCurrentPage - 1, 1));
  };

  const goToNextPage = (event) => {
    setCurrentPage((prevCurrentPage) => Math.min(prevCurrentPage + 1, totalPages));
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
  }

  const handleCloseModal = () => {
    setIsModalOpen(false);
  }

  // Update total pages and reset current page when data or search term changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, data]);

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentItems = filteredData.slice(startIndex, endIndex);

  return (
    <div className="relative overflow-x-auto sm:rounded-lg"> 
      <div className="pb-4 bg-white">
        <label htmlFor="table-search" className="sr-only">Search</label>
        <div className="relative mt-1">
          <div className="absolute inset-y-0 rtl:inset-r-0 start-0 flex items-center pl-3 pointer-events-none">
            <svg className="w-4 h-4 text-gray-500" aria-hidden="true" fill="none" viewBox="0 0 20 20">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
            </svg>
          </div>
          <input 
            type="text" 
            id="table-search" 
            className="block w-80 rounded-lg border border-gray-300 bg-gray-50 p-2 pl-10 text-sm text-gray-900 placeholder-gray-500 focus:ring-red-500 focus:border-red-500" 
            placeholder="Search for Test Name" 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      <table className="w-full text-sm text-center rtl:text-right text-gray-500">
        <thead className="text-xs text-gray-700 uppercase bg-gray-200">
          <tr>
            <th scope="col" className="px-6 py-3">Test Name</th>
            <th scope="col" className="px-6 py-3">Date</th>
            <th scope="col" className="px-6 py-3">Material</th>
            <th scope="col" className="px-6 py-3">Density</th>
            <th scope="col" className="px-6 py-3">Specific Heat Capacity</th>
            <th scope="col" className="px-6 py-3">TC Distance</th>
            <th scope="col" className="px-6 py-3">Diffusivity</th>
            <th scope="col" className="px-6 py-3">Conductivity</th>
            <th scope="col" className="px-6 py-3">Action</th>
          </tr>
        </thead>
        <tbody>
          {currentItems.filter((item) => {
            return searchTerm.toLowerCase() === '' ? item : item.testName.
            toLowerCase().includes(searchTerm);
          }).map((row) => (
            <tr key={row.testId} className="bg-white border-b">
        
              <td className="px-6 py-4">{row.testName}</td>
              <td className="px-6 py-4">{row.datetime}</td>
              <td className="px-6 py-4">{row.material}</td>
              <td className="px-6 py-4">{row.density}</td>
              <td className="px-6 py-4">{row.specificHeatCapacity}</td>
              <td className="px-6 py-4">{row.tcDistance}</td>
              <td className="px-6 py-4">{row.diffusivity}</td>
              <td className="px-6 py-4">{row.conductivity}</td>
              <td className="px-6 py-4">
              
                <a href={'/previous-jobs/' + row.testId} className="font-medium text-red-600 hover:underline" >Edit</a>
                <a href="#" 
                  onClick={handleOpenModal} 
                  className="font-medium text-red-600 hover:underline ml-2">
                  Delete
                </a>
                {isModalOpen && (
                <Modal 
                  action="Delete Test"
                  onCancel={handleCloseModal}
                  onSubmit={(event) => {
                    handleDelete(row.testId, event);
                    handleCloseModal();
                  }} 
                />                
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
        <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-gray-700">
              Showing <span className="font-medium">{startIndex + 1}</span> to <span className="font-medium">{Math.min(endIndex, data.length)}</span> of{' '}
              <span className="font-medium">{data.length}</span> results
            </p>
          </div>
          <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
            <a
              href='#'
              onClick={goToPreviousPage}
              className={`relative inline-flex items-center rounded-l-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 ${
                currentPage === 1 ? ' cursor-not-allowed opacity-50' : ''
              }`}
            >
              <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
              <span className="sr-only">Previous</span>
            </a>
            {Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => (
              <a
                key={number}
                href="#"
                onClick={(event) => goToPage(number, event)}
                className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${
                  currentPage === number
                    ? 'bg-red-600 text-white'
                    : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
                } focus:z-20 focus:outline-offset-0`}
              >
                {number}
              </a>
              ))}
            <a
              href='#'
              onClick={goToNextPage}
              className={`relative inline-flex items-center rounded-r-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 ${
                currentPage === totalPages ? ' cursor-not-allowed opacity-50' : ''
              }`}
            >
              <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
              <span className="sr-only">Next</span>
            </a>
          </nav>
        </div>
      </div>
    </div>
  );
};

export default TableComponent;

