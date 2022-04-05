module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  variants: {
    extend: {
      transitionProperty: ['hover', 'group-hover',  'focus', 'active'],
    }
  },
  plugins: [],
}
