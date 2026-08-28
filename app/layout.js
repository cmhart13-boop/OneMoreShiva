import "./globals.css";

export const metadata = {
  title: "Shiva — Fantasy Football Intelligence",
  description: "One More Shiva fantasy football intelligence"
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#071019",
  colorScheme: "dark"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head><link rel="preload" href="/shiva-trophy.png" as="image" /></head>
      <body>{children}</body>
    </html>
  );
}
