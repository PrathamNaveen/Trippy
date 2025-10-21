import './globals.css';
import { ReactNode } from 'react';

export const metadata = {
  title: 'Italy Trip Chat',
  description: 'Chat interface to ask questions about your Italy trip',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="flex flex-col h-screen bg-gray-100">
        <header className="bg-blue-600 text-white p-4 text-center font-bold">
          Italy Trip Chat
        </header>
        <main className="flex-1 overflow-y-auto">{children}</main>
      </body>
    </html>
  );
}
