import "./globals.css";
export const metadata={title:"One More Shiva",description:"Fantasy football intelligence for ESPN full-PPR leagues.",applicationName:"One More Shiva",appleWebApp:{capable:true,statusBarStyle:"black-translucent",title:"Shiva"}};
export const viewport={width:"device-width",initialScale:1,maximumScale:1,viewportFit:"cover",themeColor:"#071426"};
export default function RootLayout({children}){return <html lang="en"><body>{children}</body></html>}
