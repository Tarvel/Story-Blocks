/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "on-primary-fixed-variant": "#4e4800",
                "surface-bright": "#fff9e5",
                "on-surface-variant": "#4a4731",
                "on-tertiary-fixed": "#002020",
                "tertiary": "#006a6a",
                "tertiary-fixed": "#6cf7f7",
                "surface-container-low": "#f9f4df",
                "surface-container-highest": "#e8e3ce",
                "on-primary-fixed": "#1f1c00",
                "surface": "#fff9e5",
                "on-secondary-container": "#d6daff",
                "surface-tint": "#676000",
                "secondary-container": "#0448ff",
                "on-primary": "#ffffff",
                "inverse-primary": "#d8ca00",
                "surface-container": "#f3eeda",
                "secondary-fixed": "#dde1ff",
                "secondary": "#0035c6",
                "on-secondary": "#ffffff",
                "error": "#ba1a1a",
                "on-secondary-fixed": "#001257",
                "on-background": "#1d1c10",
                "on-tertiary": "#ffffff",
                "on-error-container": "#93000a",
                "on-error": "#ffffff",
                "on-secondary-fixed-variant": "#0033c0",
                "surface-variant": "#e8e3ce",
                "error-container": "#ffdad6",
                "secondary-fixed-dim": "#b9c3ff",
                "on-tertiary-fixed-variant": "#004f50",
                "inverse-on-surface": "#f6f1dc",
                "primary-fixed": "#f7e600",
                "outline": "#7b785f",
                "outline-variant": "#ccc7aa",
                "surface-container-high": "#ede8d4",
                "inverse-surface": "#333123",
                "tertiary-fixed-dim": "#49dada",
                "primary-fixed-dim": "#d8ca00",
                "tertiary-container": "#75ffff",
                "on-tertiary-container": "#007676",
                "surface-container-lowest": "#ffffff",
                "primary": "#676000",
                "on-surface": "#1d1c10",
                "surface-dim": "#dfdac6",
                "background": "#fff9e5",
                "on-primary-container": "#736b00",
                "primary-container": "#ffee00"
            },
            borderRadius: {
                DEFAULT: "0",
                lg: "0",
                xl: "0",
                full: "9999px"
            },
            fontFamily: {
                metadata: ["Space Grotesk"],
                "display-xl": ["Epilogue"],
                "headline-md": ["Epilogue"],
                "headline-lg": ["Epilogue"],
                "body-lg": ["Space Grotesk"],
                "body-md": ["Space Grotesk"]
            },
            fontSize: {
                metadata: ["14px", { lineHeight: "1.2", fontWeight: "500" }],
                "display-xl": ["80px", { lineHeight: "1.0", letterSpacing: "-0.04em", fontWeight: "900" }],
                "headline-md": ["32px", { lineHeight: "1.2", fontWeight: "800" }],
                "headline-lg": ["48px", { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "800" }],
                "body-lg": ["20px", { lineHeight: "1.5", fontWeight: "400" }],
                "body-md": ["16px", { lineHeight: "1.5", fontWeight: "400" }]
            }
        }
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/container-queries'),
    ],
}
