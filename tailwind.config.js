/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./budge/pages/**/*.py", // scans all Python files in the pages directory
    "./budge/components/**/*.py", // scans all Python files in the components directory
    "./budge/app/**/*.py", // scans all Python files in the app directory
    "./budge/app.py", // scans all Python files in the lib directory
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
