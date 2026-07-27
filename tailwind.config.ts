import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: "var(--accent-color)",
        offwhite: "var(--offwhite)",
        offblack: "var(--offblack)",
      },
      fontFamily: {
        sans: ['"PP Neue Montreal"', "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
