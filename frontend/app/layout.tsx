import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LegalEase",
  description: "Plain-language analysis of legal documents, grounded in Indian law.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-brand-bg">
        <header className="flex items-center justify-between border-b border-brand-border px-6 py-4">
          <Link href="/" className="font-semibold text-brand-dark">
            LegalEase
          </Link>
          <nav className="flex gap-6 text-sm font-medium text-brand-text">
            <Link href="/whatsapp-demo" className="hover:text-brand-primary">
              WhatsApp
            </Link>
            <Link href="/about" className="hover:text-brand-primary">
              About
            </Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
