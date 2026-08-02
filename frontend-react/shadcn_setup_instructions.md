# Shadcn/ui, Tailwind CSS & TypeScript Setup Instructions

This document provides step-by-step instructions on how to fully configure the `PrepSmart` React+Vite codebase to support Tailwind CSS, TypeScript, and the `shadcn/ui` CLI.

---

## 📦 Step 1: Migrate to TypeScript

Vite handles TypeScript transpilation out of the box, but you should install TypeScript and its types, and configure a `tsconfig.json` for proper IDE auto-completion and compile-time type-checking.

1. **Install TypeScript dependencies:**
   ```bash
   npm install -D typescript @types/react @types/react-dom @types/node vite-tsconfig-paths
   ```

2. **Initialize TypeScript configuration:**
   Create a `tsconfig.json` at the root of your `frontend-react` folder:
   ```json
   {
     "compilerOptions": {
       "target": "ES2020",
       "useDefineForClassFields": true,
       "lib": ["DOM", "DOM.Iterable", "ES2020"],
       "module": "ESNext",
       "skipLibCheck": true,

       /* Bundler mode */
       "moduleResolution": "bundler",
       "allowImportingTsExtensions": true,
       "resolveJsonModule": true,
       "isolatedModules": true,
       "noEmit": true,
       "jsx": "react-jsx",

       /* Linting */
       "strict": true,
       "noUnusedLocals": true,
       "noUnusedParameters": true,
       "noFallthroughCasesInSwitch": true,

       /* Path Alias */
       "baseUrl": ".",
       "paths": {
         "@/*": ["./src/*"]
       }
     },
     "include": ["src"],
     "references": [{ "path": "./tsconfig.node.json" }]
   }
   ```

3. **Configure `tsconfig.node.json`:**
   ```json
   {
     "compilerOptions": {
       "composite": true,
       "skipLibCheck": true,
       "module": "ESNext",
       "moduleResolution": "bundler",
       "allowSyntheticDefaultImports": true,
       "strict": true
     },
     "include": ["vite.config.js"]
   }
   ```

4. **Rename files:**
   Rename files like `main.jsx` and `App.jsx` to `main.tsx` and `App.tsx` when you're ready to migrate type checking.

---

## 🎨 Step 2: Install and Configure Tailwind CSS

Vite projects can integrate Tailwind CSS v4 or v3. Here is the configuration for Tailwind CSS:

1. **Install Tailwind CSS and its Vite plugin:**
   ```bash
   npm install tailwindcss @tailwindcss/vite
   ```

2. **Add Tailwind CSS plugin in `vite.config.js`:**
   ```javascript
   import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'
   import tailwindcss from '@tailwindcss/vite'
   import path from 'path'

   export default defineConfig({
     plugins: [react(), tailwindcss()],
     resolve: {
       alias: {
         '@': path.resolve(__dirname, './src'),
       },
       extensions: ['.mjs', '.js', '.mts', '.ts', '.jsx', '.tsx', '.json'],
     },
     // ...
   })
   ```

3. **Import Tailwind CSS in `src/index.css`:**
   At the very top of `src/index.css`, add:
   ```css
   @import "tailwindcss";
   ```

---

## ⚡ Step 3: Setup shadcn/ui CLI

Once TypeScript and Tailwind CSS are ready, you can configure the shadcn project structure.

1. **Initialize shadcn/ui config:**
   Run the following CLI command at the root of `frontend-react`:
   ```bash
   npx shadcn@latest init
   ```

2. **Choose Configuration Settings:**
   During the interactive prompt, select these values:
   - **Style:** `Default`
   - **Base color:** `Slate` (or your preferred theme)
   - **CSS variables:** `Yes`
   - **Tailwind CSS file location:** `src/index.css`
   - **Path alias for components:** `@/components`
   - **Path alias for utils:** `@/lib/utils`

3. **Using the CLI to add components:**
   Now you can add components directly from the shadcn registry:
   ```bash
   npx shadcn@latest add button badge card
   ```

---

## 📁 Why Creating `/src/components/ui/` Is Crucial

Shadcn components are designed to be copy-pasted directly into your codebase rather than consumed as a black-box NPM package dependency. 
Creating a dedicated `src/components/ui/` folder:
1. **Separates Concerns:** Segregates generic reusable primitives (buttons, inputs, cards) from application workflows (dashboard widgets, sidebar layout, pages).
2. **Registry Standard:** The shadcn CLI assumes a default path of `@/components/ui` to install elements, avoiding messy namespace conflicts and ensuring easy updates.
3. **Tailwind Customizability:** Allows developer customization of each local atomic component style directly without overrides.
