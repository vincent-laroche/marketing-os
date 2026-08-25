import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Social Studio | Hair Solutions Co. Marketing OS",
  description: "Hair Solutions Co. Social Studio for governed content planning, creative review, content calendars, and production systems.",
  robots: {
    index: false,
    follow: false
  },
  icons: {
    icon: "/favicon.svg"
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
