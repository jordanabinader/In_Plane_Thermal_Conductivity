'use client';
import Link from 'next/link';
import React, { useEffect } from 'react';
import ScrollToTest from './ScrollToTest';

export default function NavBar() {
    useEffect(() => {
        if (window.location.hash === '#scrollToBottom') {
          window.scroll({
            top: document.body.offsetHeight,
            left: 0, 
            behavior: 'smooth',
          });
        }
      }, []);
      
    return (
        <div className="min-h-full">
            <nav className="bg-gray-500 fixed top-0 left-0 w-full z-50">
                <div className="mx-auto max-w-1xl px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        <div className="flex w-full items-center">
                            <div className="flex-none mx-4 justify-start">
                                <img className="h-32 w-32" src="/Northeastern_Wordmark.svg" alt="Northeastern University" />
                            </div>
                            <div className="hidden md:flex justify-center">
                                <div className="flex items-baseline space-x-4">
                                    <ScrollToTest />
                                    <Link href="/" className="text-gray-300 hover:bg-gray-700 hover:text-white rounded-md px-3 py-2 text-sm font-medium">Home</Link>
                                    <Link href="/previous-jobs" className="text-gray-300 hover:bg-gray-700 hover:text-white rounded-md px-3 py-2 text-sm font-medium">Previous Jobs</Link>
                                </div>                                  
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
        </div>

    );
  }
  