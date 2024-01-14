import React from 'react'

const Footer = () => {
  return (
  <footer className="footer mt-auto footer-center grid grid-cols-2 gap-4 p-6 bg-gray-300 text-base-content rounded">
    <aside>
      <p>Copyright © 2023 - All right reserved by Northeastern University</p>
    </aside>  
    <nav className="grid grid-flow-col gap-4">
      <a href="https://www.dapslab.com/" className="link link-hover">DAPS Lab</a>
      <a href="https://www.northeastern.edu/" className="link link-hover">Northeastern University</a>
      <a href="https://pubmed.ncbi.nlm.nih.gov/36725582/#:~:text=The%20%C3%85ngstr%C3%B6m%20method%20is%20a,testing%20robustness%20of%20thermal%20conductivity." className="link link-hover">Ångström method</a>
    </nav>  

  </footer>
  )
}

export default Footer
