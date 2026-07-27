import type { Metadata, Viewport } from "next";
import "./globals.css";
import ClientLayout from "@/components/ClientLayout";

const BASE_URL = "https://ultimate-media-downloader.fun";

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f4f1ee" },
    { media: "(prefers-color-scheme: dark)", color: "#3a3a38" },
  ],
  colorScheme: "light dark",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  metadataBase: new URL(BASE_URL),

  // ── Core ─────────────────────────────────────────────────────────────────
  title: {
    default: "Ultimate Media Downloader — Download from 1000+ Platforms",
    template: "%s | Ultimate Media Downloader",
  },
  description:
    "UMD is a powerful open-source CLI tool to download videos, audio, playlists, and more from 1000+ platforms including YouTube, Twitter, Instagram, TikTok, Spotify, and Reddit.",
  keywords: [
    "media downloader",
    "video downloader",
    "youtube downloader",
    "tiktok downloader",
    "instagram downloader",
    "twitter downloader",
    "spotify downloader",
    "reddit downloader",
    "audio downloader",
    "playlist downloader",
    "open source downloader",
    "CLI media tool",
    "UMD",
    "ultimate media downloader",
    "yt-dlp alternative",
    "download videos offline",
    "download music offline",
    "1000 platforms downloader",
  ],
  authors: [{ name: "NK2552003", url: "https://github.com/NK2552003" }],
  creator: "NK2552003",
  publisher: "NK2552003",
  category: "Technology",

  // ── Robots ───────────────────────────────────────────────────────────────
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      noimageindex: false,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },

  // ── Open Graph ───────────────────────────────────────────────────────────
  openGraph: {
    type: "website",
    locale: "en_US",
    url: BASE_URL,
    siteName: "Ultimate Media Downloader",
    title: "Ultimate Media Downloader — Download from 1000+ Platforms",
    description:
      "Download videos, audio, playlists, and more from 1000+ platforms with one command. YouTube, TikTok, Instagram, Spotify, Twitter and many more.",
    images: [
      {
        url: `${BASE_URL}/og-image.jpg`,
        width: 1200,
        height: 630,
        alt: "Ultimate Media Downloader — Download from 1000+ Platforms",
        type: "image/jpeg",
      },
    ],
  },

  // ── Twitter / X Card ─────────────────────────────────────────────────────
  twitter: {
    card: "summary_large_image",
    site: "@UltimateMediaDL",
    creator: "@UltimateMediaDL",
    title: "Ultimate Media Downloader — Download from 1000+ Platforms",
    description:
      "Download videos, audio & playlists from 1000+ platforms with one command. Open-source CLI tool.",
    images: [`${BASE_URL}/og-image.jpg`],
  },

  // ── Favicons & Icons ──────────────────────────────────────────────────────
  icons: {
    icon: [
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/icons/icon-48x48.png", sizes: "48x48", type: "image/png" },
      { url: "/icons/icon-96x96.png", sizes: "96x96", type: "image/png" },
      { url: "/icons/icon-192x192.png", sizes: "192x192", type: "image/png" },
      { url: "/icons/icon-512x512.png", sizes: "512x512", type: "image/png" },
    ],
    shortcut: [{ url: "/favicon-32x32.png", type: "image/png" }],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
      { url: "/icons/icon-152x152.png", sizes: "152x152", type: "image/png" },
      { url: "/icons/icon-144x144.png", sizes: "144x144", type: "image/png" },
    ],
    other: [
      {
        rel: "mask-icon",
        url: "/icons/icon-512x512.png",
        color: "#3a3a38",
      },
      {
        rel: "msapplication-TileImage",
        url: "/icons/icon-144x144.png",
      },
    ],
  },

  // ── Web App Manifest ─────────────────────────────────────────────────────
  manifest: "/manifest.json",

  // ── Alternate / Canonical ─────────────────────────────────────────────────
  alternates: {
    canonical: BASE_URL,
    languages: {
      "en-US": BASE_URL,
    },
  },

  // ── Verification (add your tokens when ready) ─────────────────────────────
  verification: {
    // google: "YOUR_GOOGLE_SEARCH_CONSOLE_TOKEN",
    // yandex: "YOUR_YANDEX_TOKEN",
    // bing: "YOUR_BING_TOKEN",
  },

  // ── App-specific ─────────────────────────────────────────────────────────
  applicationName: "Ultimate Media Downloader",
  referrer: "origin-when-cross-origin",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Microsoft Tile Color */}
        <meta name="msapplication-TileColor" content="#f4f1ee" />
        <meta name="msapplication-config" content="/browserconfig.xml" />

        {/* Safari Pinned Tab */}
        <link rel="mask-icon" href="/icons/icon-512x512.png" color="#3a3a38" />

        {/* Schema.org Structured Data — SoftwareApplication */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              name: "Ultimate Media Downloader",
              alternateName: "UMD",
              applicationCategory: "UtilitiesApplication",
              applicationSubCategory: "Media Downloader",
              operatingSystem: "Windows, macOS, Linux",
              url: BASE_URL,
              description:
                "UMD is a powerful open-source CLI tool to download videos, audio, playlists, and more from 1000+ platforms including YouTube, Twitter, Instagram, TikTok, Spotify, and Reddit.",
              offers: {
                "@type": "Offer",
                price: "0",
                priceCurrency: "USD",
              },
              softwareVersion: "latest",
              downloadUrl: "https://codeberg.org/nk2552003/umd",
              featureList: [
                "Download from 1000+ platforms",
                "Video and audio download",
                "Playlist support",
                "Format selection",
                "Subtitle download",
                "Thumbnail download",
                "Cross-platform CLI",
              ],
              screenshot: `${BASE_URL}/og-image.jpg`,
              image: `${BASE_URL}/og-image.jpg`,
              keywords:
                "media downloader, video downloader, youtube downloader, tiktok downloader, open source",
            }),
          }}
        />

        {/* Schema.org — WebSite with SearchAction */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebSite",
              name: "Ultimate Media Downloader",
              url: BASE_URL,
              potentialAction: {
                "@type": "SearchAction",
                target: {
                  "@type": "EntryPoint",
                  urlTemplate: `${BASE_URL}/docs?q={search_term_string}`,
                },
                "query-input": "required name=search_term_string",
              },
            }),
          }}
        />

        {/* Schema.org — Organization */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Organization",
              name: "Ultimate Media Downloader",
              url: BASE_URL,
              logo: `${BASE_URL}/umd_logo.png`,
              founder: {
                "@type": "Person",
                name: "NK2552003",
                url: "https://github.com/NK2552003",
              },
              sameAs: [
                "https://github.com/NK2552003",
                "https://codeberg.org/nk2552003/umd",
              ],
            }),
          }}
        />
      </head>
      <body>
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
