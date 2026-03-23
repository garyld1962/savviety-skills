import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'App',
  description: 'Scaffolded with ts-monorepo template',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-zinc-950 text-zinc-100 antialiased">
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
