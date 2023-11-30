import { Inter } from 'next/font/google'
import './globals.css'
import Footer from '@/components/Footer';
import NavBar from '@/components/Nav';

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'THE ANGSTRONOMERS',
  description: 'Device for in-plane thermal conductivity testing using the Angstrom method',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      
      <body className={inter.className}>
        {children}
        <Footer/>
      </body>

    </html>
  )
}
