import React from "react";
import "./globals.css";

export const metadata = {
  title: "G.O.A.T Bot",
  description: "A divine AI experience powered by the wisdom of Lord Ganesha",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}