import React from 'react';


export default function NavBar() {
      
    return (
        <div className="min-h-full">
            <nav className="bg-gray-500 fixed top-0 left-0 w-full z-50">
                <div className="mx-auto max-w-1xl px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        <div className="flex w-full items-center">
                            <div className="flex-none mx-4 justify-start">
                                <img className="h-32 w-32" src="/Northeastern_Wordmark.svg" alt="Northeastern University" />
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
        </div>

    );
  }
  