'use client';
import { Fragment, useState, useEffect } from 'react'
import { Dialog, Disclosure, Menu, Transition } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { ChevronDownIcon, FunnelIcon, MinusIcon, PlusIcon, Squares2X2Icon } from '@heroicons/react/20/solid'
import PreviousJobsTable from './PreviousJobsTable'
import axios from 'axios';

const sortOptions = [
  { name: 'Date', href: '#', current: true },
  { name: 'Conductivity', href: '#', current: false },
  { name: 'Diffusivity', href: '#', current: false },
  { name: 'Density', href: '#', current: false },
  { name: 'Specific Heat', href: '#', current: false },
  { name: 'TC Distance', href: '#', current: false },
]
const initialFilters = [
  {
    id: 'conductivity',
    name: 'Conductivity',
    range: { min: '', max: '' },
  },
  {
    id: 'diffusivity',
    name: 'Diffusivity',
    range: { min: '', max: '' },
  },
  {
    id: 'material',
    name: 'Material',
    searchTerm: '',
  },
  {
    id: 'density',
    name: 'Density',
    range: { min: '', max: '' },
  },
  {
    id: 'specificHeatCapacity',
    name: 'Specific Heat',
    range: { min: '', max: '' }, 
  },
  {
    id: 'tcDistance',
    name: 'Thermocouple Distance',
    range: { min: '', max: '' }, 
  },
]

export default function FilterTable() {

  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)
  const [filters, setFilters] = useState(initialFilters);
  const [originalData, setOriginalData] = useState([]);
  const [data, setData] = useState([]);

  const fetchData = async () => {
    try {
      const response = await axios.get(`http://localhost:2999/queryAllRows/test_directory`);
      setOriginalData(response.data);
      setData(response.data)
    } catch (err) {
      console.log(err.message)
    }
  };

  useEffect(() => {
    fetchData();
    }, []); 

  useEffect(() => {
    filterData()
  }, [filters])
  
  const handleChange = (id, value, type) => {
    const updatedFilters = filters.map(f => {
      if (f.id === id) {
        if (type === 'min' || type === 'max') {
          return { ...f, range: { ...f.range, [type]: value } };
        } else if (type === 'searchTerm') {
          return { ...f, searchTerm: value };
        }
      }
      return f;
    });
    setFilters(updatedFilters);
  };

  const filterData = () => {
    let filteredData = [...originalData];

    filters.forEach(filter => {
      if (filter.searchTerm) {
        filteredData = filteredData.filter((item) => {
          return filter.searchTerm.toLowerCase() === '' ? true : item[filter.id].toLowerCase().includes(filter.searchTerm.toLowerCase());
        });
      } 
      if (filter.range) {
        filteredData = filteredData.filter(item => {
          // Check if the value is empty or null, and if so, do not filter it out
          if (item[filter.id] === null || item[filter.id] === '') {
            return true;
          }
      
          const value = parseFloat(item[filter.id]);
          // Handle cases where parseFloat returns NaN
          if (isNaN(value)) {
            return true;
          }
      
          const min = filter.range.min !== '' ? parseFloat(filter.range.min) : -Infinity;
          const max = filter.range.max !== '' ? parseFloat(filter.range.max) : Infinity;
      
          return value >= min && value <= max;
        });
      }
    });
    if (filterData.lenth !== 0) {
      setData(filteredData);
    } 
  };

  const handleDelete = async (testId, event) => {
    event.preventDefault();
    try {
      const response = await axios.delete(`http://localhost:2999/deleteTest/${testId}`);
      console.log(response)
      if (response.status === 200) {
        fetchData()
        console.log('Test successfully deleted');
      }
    } catch (error) {
      // Handle error here (e.g., showing an error message)
      console.error('Error deleting test:', error.message);
    }
  };

  return (
    <div className="bg-white">
      <div>
        {/* Mobile filter dialog */}
        <Transition.Root show={mobileFiltersOpen} as={Fragment}>
          <Dialog as="div" className="relative z-40 lg:hidden" onClose={setMobileFiltersOpen}>
            <Transition.Child
              as={Fragment}
              enter="transition-opacity ease-linear duration-300"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="transition-opacity ease-linear duration-300"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <div className="fixed inset-0 bg-black bg-opacity-25" />
            </Transition.Child>

            <div className="fixed inset-0 z-40 flex">
              <Transition.Child
                as={Fragment}
                enter="transition ease-in-out duration-300 transform"
                enterFrom="translate-x-full"
                enterTo="translate-x-0"
                leave="transition ease-in-out duration-300 transform"
                leaveFrom="translate-x-0"
                leaveTo="translate-x-full"
              >
                <Dialog.Panel className="relative ml-auto flex h-full w-full max-w-xs flex-col overflow-y-auto bg-white py-4 pb-12 shadow-xl">
                  <div className="flex items-center justify-between px-4">
                    <h2 className="text-lg font-medium text-gray-900">Filters</h2>
                    <button
                      type="button"
                      className="-mr-2 flex h-10 w-10 items-center justify-center rounded-md bg-white p-2 text-gray-400"
                      onClick={() => setMobileFiltersOpen(false)}
                    >
                      <span className="sr-only">Close menu</span>
                      <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                    </button>
                  </div>

                  {/* Filters */}
                  <form className="mt-4 border-t border-gray-200">
                    {filters.map((section) => (
                      <Disclosure as="div" key={section.id} className="border-t border-gray-200 px-4 py-6">
                        {({ open }) => (
                          <>
                            <h3 className="-mx-2 -my-3 flow-root">
                              <Disclosure.Button className="flex w-full items-center justify-between bg-white px-2 py-3 text-gray-400 hover:text-gray-500">
                                <span className="font-medium text-gray-900">{section.name}</span>
                                <span className="ml-6 flex items-center">
                                  {open ? (
                                    <MinusIcon className="h-5 w-5" aria-hidden="true" />
                                  ) : (
                                    <PlusIcon className="h-5 w-5" aria-hidden="true" />
                                  )}
                                </span>
                              </Disclosure.Button>
                            </h3>
                            <Disclosure.Panel className="pt-6">
                                <div className="space-y-6">
                                    {section.options ? (
                                        section.options.map((option, optionIdx) => (
                                        <div key={option.value} className="flex items-center">
                                            <input
                                            id={`filter-mobile-${section.id}-${optionIdx}`}
                                            name={`${section.id}[]`}
                                            value={option.value}
                                            type="checkbox"
                                            chacked={option.checked}
                                            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                                            />
                                            <label
                                            htmlFor={`filter-mobile-${section.id}-${optionIdx}`}
                                            className="ml-3 text-sm text-gray-600"
                                            >
                                            {option.label}
                                            </label>
                                        </div>
                                        ))
                                    ) : section.searchTerm !== undefined ? (
                                        <input
                                        type="text"
                                        className="binput input-bordered w-full max-w-xs text-sm"
                                        placeholder={`Search ${section.name}`}
                                        value={section.searchTerm}
                                        onChange={(e) => handleChange(section.id, e.target.value, 'searchTerm')}
                                        />
                                    ) : (
                                        <div className="flex space-max">
                                            <div className="form-control w-1/4">
                                                <label className="label">
                                                    <span className="label-text mx-4 text-sm">Min.</span>
                                                </label>
                                                <input 
                                                type="text" 
                                                placeholder="0.00" 
                                                className="input input-bordered" 
                                                value={section.range.min}
                                                onChange={(e) => handleChange(section.id, e.target.value, 'min')}
                                                />
                                            </div>

                                            <div className="ml-32 form-control w-1/4">
                                                <label className="label">
                                                    <span className="label-text mx-4 text-sm">Max.</span>
                                                </label>
                                                <input 
                                                type="text" 
                                                placeholder="0.00" 
                                                className="input input-bordered" 
                                                value={section.range.max}
                                                onChange={(e) => handleChange(section.id, e.target.value, 'max')}
                                                />
                                            </div>
                                        </div>  
                                    )}
                                </div>
                            </Disclosure.Panel>
                          </>
                        )}
                      </Disclosure>
                    ))}
                  </form>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </Dialog>
        </Transition.Root>

        <main className="mx-auto max-w-full  sm:px-10 lg:px-12">
          <div className="flex items-baseline justify-between border-b border-gray-200 pb-6 pt-24">
            <h1 className="text-4xl font-bold tracking-tight text-gray-700">Previous Jobs</h1>
            <div className="flex items-center">
              <Menu as="div" className="relative inline-block text-left">
                <div>
                  <Menu.Button className="group inline-flex justify-center text-sm font-medium text-gray-700 hover:text-gray-900">
                    Sort by
                    <ChevronDownIcon
                      className="-mr-1 ml-1 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-500"
                      aria-hidden="true"
                    />
                  </Menu.Button>
                </div>

                <Transition
                  as={Fragment}
                  enter="transition ease-out duration-100"
                  enterFrom="transform opacity-0 scale-95"
                  enterTo="transform opacity-100 scale-100"
                  leave="transition ease-in duration-75"
                  leaveFrom="transform opacity-100 scale-100"
                  leaveTo="transform opacity-0 scale-95"
                >
                  <Menu.Items className="absolute right-0 z-10 mt-2 w-40 origin-top-right rounded-md bg-white shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div className="py-1">
                      {sortOptions.map((option) => (
                        <Menu.Item key={option.name}>
                          {({ active }) => (
                            <a
                              href={option.href}
                              className={classNames(
                                option.current ? 'font-medium text-gray-900' : 'text-gray-500',
                                active ? 'bg-gray-100' : '',
                                'block px-4 py-2 text-sm'
                              )}
                            >
                              {option.name}
                            </a>
                          )}
                        </Menu.Item>
                      ))}
                    </div>
                  </Menu.Items>
                </Transition>
              </Menu>
              <button
                type="button"
                className="-m-2 ml-4 p-2 text-gray-400 hover:text-gray-500 sm:ml-6 lg:hidden"
                onClick={() => setMobileFiltersOpen(true)}
              >
                <span className="sr-only">Filters</span>
                <FunnelIcon className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>
          </div>

          <section aria-labelledby="tests-heading" className="pb-5 pt-2">
            <div className="grid grid-cols-1 gap-x-8 gap-y-10 lg:grid-cols-[300px_minmax(600px,_2fr)]">
              {/* Filters */}
              <form className="hidden lg:block">
                {filters.map((section) => (
                  <Disclosure as="div" key={section.id} className="border-b border-gray-200 py-6">
                    {({ open }) => (
                      <>
                        <h3 className="-my-3 flow-root">
                          <Disclosure.Button className="flex w-full items-center justify-between bg-white py-3 text-sm text-gray-400 hover:text-red-500">
                            <span className="font-medium text-gray-900">{section.name}</span>
                            <span className="ml-6 flex items-center">
                              {open ? (
                                <MinusIcon className="h-5 w-5" aria-hidden="true" />
                              ) : (
                                <PlusIcon className="h-5 w-5" aria-hidden="true" />
                              )}
                            </span>
                          </Disclosure.Button>
                        </h3>
                        <Disclosure.Panel className="pt-6">
                            <div className="space-y-6">
                                    {section.options ? (
                                        section.options.map((option, optionIdx) => (
                                        <div key={option.value} className="flex items-center">
                                            <input
                                            id={`filter-mobile-${section.id}-${optionIdx}`}
                                            name={`${section.id}[]`}
                                            defaultValue={option.value}
                                            type="checkbox"
                                            defaultChecked={option.checked}
                                            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                                            />
                                            <label
                                            htmlFor={`filter-mobile-${section.id}-${optionIdx}`}
                                            className="ml-3 text-sm text-gray-600"
                                            >
                                            {option.label}
                                            </label>
                                        </div>
                                        ))
                                    ) : section.searchTerm !== undefined ? (
                                        <input
                                        type="text"
                                        className="input input-bordered w-full max-w-xs text-sm"
                                        placeholder={`Search ${section.name}`}
                                        value={section.searchTerm}
                                        onChange={(e) => handleChange(section.id, e.target.value, 'searchTerm')}
                                        />
                                    ) : (
                                        <div className="flex">
                                            <div className="form-control ml-1.5 w-1/4">
                                                <label className="label">
                                                    <span className="label-text mx-4">Min.</span>
                                                </label>
                                                <input 
                                                type="text" 
                                                placeholder="0.00" 
                                                className="input input-bordered text-sm" 
                                                value={section.range.min}
                                                onChange={(e) => handleChange(section.id, e.target.value, 'min')}
                                                />
                                            </div>

                                            <div className="ml-32 form-control w-1/4">
                                                <label className="label">
                                                    <span className="label-text mx-4">Max.</span>
                                                </label>
                                                <input 
                                                type="text" 
                                                placeholder="inf" 
                                                className="input input-bordered text-sm" 
                                                value={section.range.max}
                                                onChange={(e) => handleChange(section.id, e.target.value, 'max')}
                                                />
                                            </div>
                                        </div>

                                    )}
                            </div>
                        </Disclosure.Panel>
                      </>
                    )}
                  </Disclosure>
                ))}
              </form>

              {/* Product grid */}
              <PreviousJobsTable data={data} handleDelete={handleDelete}/>         
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}
