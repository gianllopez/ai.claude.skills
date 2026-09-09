---
title: Tipografías a través de la API integrada
impact: HIGH
description: Exige que las fuentes web se declaren en la configuración fonts y se rendericen con el componente Font, que las autoaloja, subconjunta, precarga y genera sus fallbacks, en lugar de usar un CDN de fuentes de terceros o declaraciones de face escritas a mano.
tags: fonts, assets, performance, privacy, tailwind
---

## Tipografías a través de la API integrada

**Impacto (HIGH):** Una fuente web está en el camino crítico del texto, así que toda decisión sobre ella es una decisión sobre cuándo la página se vuelve legible. Cargarla desde un _CDN_ de fuentes de terceros cuesta una resolución _DNS_, una conexión y una ida y vuelta a un origen que el sitio no controla, antes de que se pueda pedir el primer glifo — y entrega la petición de cada visitante a ese tercero, lo que en varias jurisdicciones es una cuestión de privacidad antes que de rendimiento. Montar la alternativa a mano es peor en otra dirección: los bloques `@font-face` escritos a mano omiten habitualmente `font-display`, así que el texto permanece invisible mientras el archivo se descarga, y omiten un fallback con métricas ajustadas, así que la página se reflowea cuando llega la tipografía real. La _API_ integrada convierte todo eso en una entrada de configuración — descarga y autoaloja el archivo, lo subconjunta, genera el fallback, define `font-display` y emite la pista de precarga.

**Directrices:**

1.  **Declara las fuentes en `fonts` dentro de `astro.config.mjs`:**
    - Cada entrada nombra un `provider`, el `name` de la familia y la `cssVariable` que usará el resto del proyecto
    - `fontProviders.fontsource()` y `fontProviders.google()` descargan en tiempo de compilación y autoalojan el resultado — la familia viene del proveedor, los bytes vienen de tu propio origen
    - Un archivo local se declara igual, así que una tipografía con licencia y una pública se configuran de forma idéntica
2.  **Renderiza `<Font />` una sola vez, en el layout base:**
    - Emite las reglas `@font-face` y las pistas de precarga de esa variable
    - `preload` corresponde a la tipografía que se renderiza por encima del pliegue, y solo a esa — precargar todos los pesos los pone a todos en el camino crítico y anula el propósito
3.  **Consume la familia a través de su variable, nunca por nombre:**
    - La `cssVariable` es la referencia única. Una hoja de estilos que además escriba `font-family: 'Inter', sans-serif` a mano tiene una segunda fuente de verdad que la configuración no puede mantener correcta
    - En un proyecto _TailwindCSS_ esta es la costura con el tema: el token de `@theme` se define como esa variable, de modo que `font-sans` resuelve a la tipografía configurada — ver la regla de configuración de _TailwindCSS_
4.  **Carga los pesos y estilos que el diseño usa, y ningún otro:**
    - Cada peso adicional es otro archivo; una fuente variable suele ser un único archivo que cubre todo el rango
    - El conjunto real del diseño es una lista corta, y enviar la familia completa porque era más fácil es un coste que se paga en cada primera visita
5.  **Qué reemplaza esto:**
    - Etiquetas `<link>` a un _CDN_ de fuentes en el head del documento
    - Bloques `@font-face` escritos a mano y los detalles de `font-display`, `unicode-range` y métricas de fallback que los acompañan
    - Archivos de fuente commiteados en `public/` y referenciados por _URL_

**Incorrecto (CDN de terceros, más una face escrita a mano que provoca reflow):**

```astro
---
// src/layouts/Base.astro
---

<head>
  <!-- Mal: resolución DNS, conexión e ida y vuelta a un origen que no controlas,
       antes de que se pida el primer glifo -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
    rel="stylesheet"
  />

  <style is:global>
    /* Mal: sin font-display, así que el texto es invisible mientras esto se
       descarga, y sin fallback con métricas ajustadas, así que la página se
       reflowea cuando llega */
    @font-face {
      font-family: 'Satoshi';
      src: url('/fonts/satoshi.woff2') format('woff2');
    }

    body {
      /* Mal: la familia nombrada a mano, en un segundo lugar */
      font-family: 'Inter', system-ui, sans-serif;
    }
  </style>
</head>
```

**Correcto (declarada una vez, autoalojada, consumida a través de su variable):**

```js
// astro.config.mjs
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  fonts: [
    {
      name: 'Inter',
      cssVariable: '--font-inter',
      provider: fontProviders.fontsource(),
      // Solo lo que el diseño usa
      weights: [400, 600],
      styles: ['normal'],
      subsets: ['latin'],
    },
  ],
});
```

```astro
---
// src/layouts/Base.astro
import { Font } from 'astro:assets';
import '../styles/global.css';
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <!-- precarga solo la tipografía que se renderiza por encima del pliegue -->
    <Font cssVariable="--font-inter" preload />
  </head>
  <body>
    <slot />
  </body>
</html>
```

```css
/* src/styles/global.css — la variable es la única referencia a la familia */
@import 'tailwindcss';

@theme {
  --font-sans: var(--font-inter), system-ui, sans-serif;
}
```

Referencia: [Fonts](https://docs.astro.build/en/guides/fonts/)
