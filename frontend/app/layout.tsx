import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/providers/providers";

export const metadata: Metadata = {
  title: "MediAssist — AI Healthcare Assistant",
  description:
    "Intelligent multi-agent AI healthcare assistant: symptom analysis, medicine information, doctor recommendations and emergency detection. Educational purposes only.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
