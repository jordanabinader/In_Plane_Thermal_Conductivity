'use client';
import React, { useState } from 'react';

const ScrollToTest = () => {

  function handleScroll() {
    if (window.location.pathname !== '/') {
        // Navigate to the root with a hash
        window.location.href = '/#scrollToBottom';
    } else {
        // If already on the root page, scroll to bottom
        window.scroll({
            top: document.body.offsetHeight,
            left: 0, 
            behavior: 'smooth',
        });
    }
  }

  return (
      <button 
        className="rounded-md bg-red-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600" 
        aria-current="page" 
        type="button" 
        onClick={handleScroll}
      >
        Test Set Up
      </button>             
)}

export default ScrollToTest;
