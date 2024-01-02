import React from 'react'

const Footer = () => {
  return (
  <footer className="footer mt-auto footer-center grid grid-cols-2 gap-4 p-6 bg-gray-300 text-base-content rounded">
    <aside>
      <p>Copyright © 2023 - All right reserved by Northeastern University</p>
    </aside>  
    <nav className="grid grid-flow-col gap-4">
      <a className="link link-hover">DAPS Lab</a>
      <a className="link link-hover">Northeastern University</a>
      <a className="link link-hover">Ångström method</a>
    </nav>  

  </footer>
  )
}

export default Footer
