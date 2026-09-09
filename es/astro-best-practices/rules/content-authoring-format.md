---
title: Markdown, MDX y el componente Code
impact: HIGH
description: Mantiene la prosa en Markdown plano y reserva MDX para el contenido que realmente incrusta componentes, renderiza con el componente Code el código dinámico en tiempo de compilación, y configura deliberadamente el procesador de Markdown de la v7.
tags: content, markdown, mdx, shiki, processor
---

## Markdown, MDX y el componente Code

**Impacto (HIGH):** _MDX_ es _Markdown_ que puede importar y ejecutar componentes, y esa capacidad no es gratis: cada archivo _MDX_ se compila como un módulo, puede meter un componente de framework en la página, y deja de ser contenido que alguien sin perfil técnico pueda editar con seguridad. Convertirlo en el formato de autoría por defecto de un blog significa que cien archivos de prosa cargan con la maquinaria que solo cuatro necesitaban. El defecto espejo es recurrir a bloques `<pre>` en crudo o a un resaltador de terceros cuando el código que se renderiza es dinámico, ignorando el resaltador que _Astro_ ya ejecuta. Y en la v7 el procesador que hay debajo de todo esto cambió: **Sätteri es el valor por defecto**, no ejecuta plugins de _remark_ ni de _rehype_, y `@astrojs/markdown-remark` ya no se instala por ti — así que un proyecto que arrastró su cadena de plugins sin tocar la configuración la ha perdido en silencio.

**Directrices:**

1.  **El _Markdown_ plano es el valor por defecto para la prosa:**
    - Artículos, páginas de documentación, entradas de changelog, textos legales — cualquier cosa que sea texto con encabezados, enlaces, listas e imágenes
    - Sigue siendo editable por cualquiera, produce diffs limpios y no puede importar un componente que cambie el coste de la página
2.  **_MDX_ cuando el contenido realmente incrusta componentes:**
    - Una demo en vivo, un gráfico interactivo dentro de un artículo, un aviso personalizado que el sitio define, un formulario incrustado
    - Instálalo deliberadamente con `npx astro add mdx`, y trata la extensión del archivo como una declaración: `.mdx` significa que esta página ejecuta componentes
    - Un componente usado en todos los artículos no es razón para convertir todos los artículos en _MDX_ — eso es un asunto del layout, y el layout ya es un componente
3.  **Los componentes dentro de _MDX_ obedecen las reglas de hidratación:**
    - Un componente `.astro` importado no cuesta nada; un componente de framework sigue necesitando una directiva `client:*` y sigue pagándose
    - La isla que más a menudo se cuela en un sitio es la que entró por un artículo
4.  **`<Code />` para el código que es dinámico en tiempo de compilación:**
    - Los bloques de código delimitados en _Markdown_ ya los resalta _Shiki_ — déjalos en paz
    - `<Code />` de `astro:components` es ese mismo resaltador en forma de componente, y es la herramienta correcta cuando la fuente es una variable, un archivo leído en tiempo de compilación o un valor de un _CMS_
    - **No** hereda `markdown.shikiConfig`. A un bloque `<Code />` que deba coincidir con el tema de los bloques delimitados que lo rodean hay que pasarle `theme` explícitamente, o la página renderiza dos temas distintos
    - `import.meta.glob()` es la forma de que un archivo de tiempo de compilación se convierta en esa variable; `Astro.glob()` se eliminó en la v6
5.  **Configura el procesador en lugar de heredarlo:**
    - **Sätteri** es el valor por defecto en la v7 y no necesita configuración; decláralo explícitamente solo cuando pases feature flags
    - Ejecuta plugins de _mdast_ y _hast_, que son su propio ecosistema — los plugins de _remark_ y _rehype_ no funcionan bajo él
    - Un proyecto con una cadena _remark_/_rehype_ existente vuelve a optar por ella con `processor: unified()` de `@astrojs/markdown-remark`, que ahora hay que instalar explícitamente
    - Las opciones de nivel superior `markdown.remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm` y `smartypants` están obsoletas en favor de opciones pasadas al procesador. Dejarlas ahí es tener una cadena que dejará de aplicarse

**Incorrecto (MDX por defecto, un bloque de código dinámico sin tema, y una cadena de plugins huérfana):**

```js
// astro.config.mjs
export default defineConfig({
  markdown: {
    // Mal: bajo el procesador por defecto de la v7 esto no se aplica — la cadena
    // está configurada, inerte, y nada lo reporta
    remarkPlugins: [remarkToc],
    gfm: true,
    shikiConfig: { theme: 'github-dark' },
  },
});
```

Después, en `src/data/blog/release-notes.mdx` — prosa escrita como _MDX_ por costumbre, con un `<Code />` que nunca recibe un tema, así que se renderiza con el tema por defecto mientras cada bloque delimitado de la página se renderiza en `github-dark`:

```jsx
import { Code } from 'astro:components';

<Code code={snippet} lang="ts" />;
```

**Correcto (formato elegido por archivo, procesador declarado, tema pasado explícitamente):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import remarkToc from 'remark-toc';

export default defineConfig({
  markdown: {
    // Este proyecto tiene una cadena remark existente, así que vuelve a optar
    // por unified en lugar de perderla en silencio bajo Sätteri (el valor
    // por defecto de la v7)
    processor: unified({ remarkPlugins: [remarkToc] }),
    shikiConfig: { theme: 'github-dark' },
  },
});
```

La misma entrada como `src/data/blog/release-notes.md` — _Markdown_ plano, sin imports, con su bloque delimitado ya resaltado por el procesador configurado:

````markdown
We shipped a few things this month.

```ts
const client = createClient({ retries: 3 });
```
````

```astro
---
// src/pages/docs/examples.astro — código dinámico en tiempo de compilación
import { Code } from 'astro:components';

const modules = import.meta.glob('../../examples/*.ts', {
  eager: true,
  query: '?raw',
  import: 'default',
});
const [path, source] = Object.entries(modules)[0];
---

<!-- tema pasado explícitamente para que coincida con los bloques delimitados del resto -->
<Code code={source} lang="ts" theme="github-dark" />
```

Referencia: [Markdown in Astro](https://docs.astro.build/en/guides/markdown-content/)
