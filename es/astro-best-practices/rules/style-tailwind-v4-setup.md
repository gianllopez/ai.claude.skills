---
title: Configuración de TailwindCSS v4 y tokens de tema
impact: HIGH
description: Instala TailwindCSS mediante el plugin de Vite en lugar de la integración de Astro obsoleta, declara los tokens de diseño en el bloque @theme, y conecta el token de tipografía con la variable que genera la Fonts API.
tags: tailwind, styling, theme, tokens, vite
---

## Configuración de TailwindCSS v4 y tokens de tema

**Impacto (HIGH):** En la v4 hay dos formas de instalar _TailwindCSS_ en un proyecto _Astro_ y solo una de ellas es la vigente: `@astrojs/tailwind` es la integración obsoleta de la era v3, y `@tailwindcss/vite` ejecuta el motor dentro de la propia cadena de _Vite_. Un proyecto en el camino antiguo obtiene una pasada de _PostCSS_ aparte, recompilaciones más lentas, y configuración en un archivo que la v4 ya no trata como fuente de verdad. Esa es la mitad de la configuración. La mitad de los tokens es aquello para lo que la configuración existe: en la v4 el tema **es** la hoja de estilos, así que un token declarado genera sus utilidades y expone una variable _CSS_ a la vez, y cada valor arbitrario escrito en un punto de llamada es una decisión de diseño tomada fuera de ese sistema. La costura específica de _Astro_ es la tipografía: la Fonts _API_ produce una variable, y el token del tema tiene que definirse como esa variable, o el proyecto tendrá dos nombres para una misma familia y ninguna garantía de que coincidan.

**Directrices:**

1.  **Instala a través de _Vite_:**
    - `tailwindcss` y `@tailwindcss/vite`, registrados como `vite: { plugins: [tailwindcss()] }` en `astro.config.mjs`
    - `@astrojs/tailwind` está obsoleto. Un proyecto que todavía lo liste en `integrations` está en el camino de la v3 y debería migrar antes de que aplique nada más de aquí
    - No hay `tailwind.config.js` por defecto; una configuración en _JS_ vuelve solo a través de `@config`, y solo cuando un plugin heredado lo requiere
2.  **Una única hoja de estilos global, importada una sola vez:**
    - `@import 'tailwindcss'` al principio de `src/styles/global.css`, y ese archivo importado en el layout base — no en cada página, ni en cada componente
    - El layout base es el punto de entrada único, lo que encaja con la regla de responsabilidad de rutas: el layout es dueño de lo que todas las páginas comparten
3.  **Declara las decisiones de diseño en `@theme`:**
    - Colores, radios, tipografías, breakpoints, sombras y escalones tipográficos viven en el bloque `@theme`, y cada token genera sus utilidades automáticamente — `--color-brand` produce `bg-brand`, `text-brand`, `border-brand`
    - La escala de espaciado es la excepción y no se vuelve a declarar: `--spacing` es de _Tailwind_, y redefinirla cambia todos los márgenes, huecos y tamaños de golpe
    - Dimensiona la capa de tokens al proyecto. Un `@theme` sencillo es un sistema completo para la mayoría de los sitios; la capa `:root` / `.dark` respaldada por variables solo se gana su indirección allí donde algo la lee — un cambio de tema, o un generador de componentes
4.  **Conecta el token de tipografía con la variable de la Fonts _API_:**
    - La `cssVariable` declarada en la configuración `fonts` es la única referencia a la familia, y `--font-sans: var(--font-inter), system-ui, sans-serif` en `@theme` es lo que hace que `font-sans` resuelva a ella
    - Nombrar la familia otra vez en _CSS_ crea una segunda fuente de verdad que la configuración de fuentes no puede mantener correcta
5.  **Los valores arbitrarios son una señal de revisión:**
    - `bg-[#1d4ed8]`, `p-[13px]`, `text-[15px]` significan o bien que el token existe y no se usó, o bien que el token falta y debería añadirse
    - La geometría genuinamente puntual — `grid-cols-[auto_1fr]`, una _URL_ de máscara, un desplazamiento de terceros — es legítima. Un color casi nunca lo es, y un valor de espaciado nunca
6.  **Deja el orden de las clases en manos del formateador:**
    - `prettier-plugin-tailwindcss` ordena los atributos de clase, incluso en archivos `.astro`, así que el orden nunca es un comentario de revisión
    - Las utilidades en conflicto dentro de una misma cadena siguen resolviéndose por orden de la hoja de estilos y no por intención, cosa que ordenar no arregla — eso es un defecto que hay que eliminar, no reordenar
7.  **Dónde se detiene esta skill:**
    - La composición de clases dentro de una isla de _React_, y el helper consciente de fusiones que la hace segura, pertenecen a las skills de _React_ que un proyecto carga junto a esta. Lo que se enuncia aquí es la configuración del proyecto y su capa de tokens

**Incorrecto (integración obsoleta, una configuración JS que la v4 no lee, tokens inventados en el punto de llamada):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind'; // integración obsoleta de la v3

export default defineConfig({
  integrations: [tailwind()],
});
```

```js
// tailwind.config.js — no es la fuente de verdad en la v4
module.exports = {
  theme: {
    extend: {
      colors: { brand: '#1d4ed8' },
      fontFamily: { sans: ['Inter', 'sans-serif'] },
    },
  },
};
```

```astro
---
// src/components/Badge.astro
---

<!-- Mal: el color de marca y el espaciado inventados aquí, y la familia
     tipográfica nombrada por segunda vez, desconectada de la variable
     de la Fonts API -->
<span
  class="rounded-[7px] bg-[#1d4ed8] px-[13px] py-[5px] text-[13px] text-white"
  style="font-family: 'Inter', sans-serif"
>
  <slot />
</span>
```

**Correcto (plugin de Vite, tokens en CSS, tipografía conectada a la variable generada):**

```js
// astro.config.mjs
import { defineConfig, fontProviders } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://example.com',
  vite: { plugins: [tailwindcss()] },
  fonts: [
    {
      name: 'Inter',
      cssVariable: '--font-inter',
      provider: fontProviders.fontsource(),
    },
  ],
});
```

```css
/* src/styles/global.css — el tema es la hoja de estilos */
@import 'tailwindcss';

@theme {
  /* La costura: el token se define como la variable que genera la Fonts API */
  --font-sans: var(--font-inter), system-ui, sans-serif;

  --color-brand: oklch(0.53 0.19 262);
  --color-brand-strong: oklch(0.44 0.19 262);
  --radius-badge: 0.4375rem;
  --text-badge: 0.8125rem;
}
```

```astro
---
// src/layouts/Base.astro — importado una vez, para todo el sitio
import { Font } from 'astro:assets';
import '@styles/global.css';
---

<html lang="en">
  <head>
    <Font cssVariable="--font-inter" preload />
  </head>
  <body class="font-sans">
    <slot />
  </body>
</html>
```

```astro
---
// src/components/Badge.astro — cada valor resuelve a través de un token
---

<span
  class="text-badge rounded-badge bg-brand px-3 py-1 text-white"
>
  <slot />
</span>
```

Referencia: [Install Tailwind CSS with Astro](https://tailwindcss.com/docs/installation/framework-guides/astro)
