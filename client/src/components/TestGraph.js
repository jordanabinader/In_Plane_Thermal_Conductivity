'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './TestGraph.module.css';
import InputField from './InputField';
import Modal from './Modal';
import stylesBox from './KpiBox.module.css'
import axios from 'axios';


const TestGraph = (testIdIn) => {
    const router = useRouter();
    const [togglePosition, setTogglePosition] = useState('left');
    const [buttonStyle, setButtonStyle] = useState({});
    const [formData, setFormData] = useState({
        frequency: 0,
        amplitude: 0,
        duty_ratio: 0,
    });
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isModal2Open, setIsModal2Open] = useState(false);

    const leftClick = () => {
        setButtonStyle({ left: '0' });
        setTogglePosition('left');
    };

    const rightClick = () => {
        setButtonStyle({ left: '110px' });
        setTogglePosition('right');
    };

    const handleTestStop = async () => {
        try {
            const response = await axios.post('http://localhost:3001/test-end');
            console.log('Test stopped successfully:', response.data);
            router.push(`/previous-jobs`);
        } catch (error) {
            console.error('Error stopping test:', error);
        }
    };

    const handleOpenModal = () => {
        setIsModalOpen(true);
    };
    const handleOpenModal2 = () => {
        setIsModal2Open(true);
    };
    const handleCloseModal = () => {
        setIsModalOpen(false);
    };
    const handleCloseModal2 = () => {
        setIsModal2Open(false);
    };

    const handleTextChange = (e) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    };
    
    const handleSubmitChanges = async (formData) => {
        handleCloseModal();
        try {
            const response = await axios.post(`http://localhost:80/changeTestSetting/${testIdIn.testIdIn}`, formData, testIdIn);
            console.log(response.data);
        
          } catch (error) {
            console.error("Error updating test setting:", error.response);
            throw error;
          }

          try {
            const response = await axios.put('http://localhost:3001/test-setting-update');
            console.log('Test changed successfully:', response.data);
        } catch (error) {
            console.error('Error changing test:', error);
        }
        };

    return (
        <div className='bg-white h-screen'>
            <div className='grid md:grid-cols-[4fr_2fr] grid-cols-1 h-1/2'>
                <div className='rounded-md'>
                    <div className="bg-gray-200 h-full">
                    <iframe
                        title="Bokeh Plot"
                        src="http://localhost:8123"
                        width="100%"
                        height="100%"
                    />
                    </div>
                    <div className="flex justify-center mt-6"> 
                        <button 
                            className="rounded-md bg-red-600 px-3.5 py-2.5 mb-4 text-md font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600" 
                            aria-current="page" 
                            type="button" 
                            onClick={handleOpenModal2}
                        >
                            Stop Test
                        </button>
                        {isModal2Open && (
                            <Modal 
                                action="Stop Test"
                                onCancel={handleCloseModal2}
                                onSubmit={handleTestStop}
                            />
                        )}
                    </div>
                </div>
                <div className='h-full'>
                    <div className={styles.body}>
                        <div className={styles.buttonBox}>
                            <div id="btn" style={buttonStyle} className={styles.btn}></div>
                            <button type="button" className={styles.toggleBtn} onClick={leftClick}>Power</button>
                            <button type="button" className={styles.toggleBtn} onClick={rightClick}>D.R. %</button>
                        </div>
                        <form>
                            {togglePosition === 'left' && (
                            <div className='flex justify-center mt-4 mb-4'>
                            <div className='w-full md:w-96 mx-auto p-4'>
                                    <InputField
                                    label="Frequency"
                                    id="frequency"
                                    name="frequency"
                                    placeholder={formData.frequency}
                                    unit='Hz'
                                    value={formData.frequency}
                                    onChange={handleTextChange}
                                    />
                                    <InputField
                                    label="Amplitude"
                                    id="amplitude"
                                    name="amplitude"
                                    placeholder={formData.amplitude}
                                    value={formData.amplitude}
                                    onChange={handleTextChange}
                                    />                        
                                </div>                        
                            </div>
                            )}
                            {togglePosition === 'right' && (
                            <div className='flex justify-center mt-4 mb-4'>
                                <div className='w-full md:w-96 mx-auto p-4'>
                                    <InputField
                                    label="Duty Ratio"
                                    id="duty_ratio"
                                    name="duty_ratio"
                                    placeholder="x"
                                    unit = '%'
                                    value={formData.duty_ratio}
                                    onChange={handleTextChange}
                                    />      
                            </div>
                                </div>
                            )}
                            <div className="flex justify-center">
                                <button 
                                className="rounded-md m-4 bg-green-500 px-3.5 py-2.5 text-md font-semibold text-white shadow-sm hover:bg-green-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
                                aria-current="page"
                                type="button"
                                onClick={handleOpenModal}
                                >
                                Submit Changes
                                </button>
                                {isModalOpen && (
                                <Modal 
                                    action="Submit Changes"
                                    onCancel={handleCloseModal}
                                    onSubmit={() => handleSubmitChanges(formData)}
                                />
                                )}
                            </div>  
                        </form>
                    </div>                    
                </div>

            </div>            
        </div>


    );
};

export default TestGraph;