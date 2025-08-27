import React from "react";
import "./globals.css";
import { ThemeProvider } from "@/components/themeprovider"

export const metadata = {
  title: "G.O.A.T Bot",
  description: "A divine AI experience powered by the wisdom of Lord Ganesha",
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <>
      <html lang="en" suppressHydrationWarning>
        <head />
        <body>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            {children}
          </ThemeProvider>
        </body>
      </html>
    </>
  )
}