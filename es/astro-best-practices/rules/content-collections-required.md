---
title: Colecciones de contenido a través de la Content Layer API
impact: CRITICAL
description: Exige que todo el contenido estructurado pase por colecciones tipadas definidas en src/content.config.ts con un loader explícito, y rechaza las formas heredadas ya eliminadas y la lectura de archivos ad hoc.
tags: content, collections, content-layer, zod, typescript
---

## Colecciones de contenido a través de la Content Layer API

**Impacto (CRITICAL):** El contenido leído a mano es contenido sin contrato. Una página que hace `post.data.title` contra un archivo _Markdown_ recogido con un glob manual obtiene `undefined` justo en la entrada donde la clave del frontmatter estaba mal escrita, renderiza un `<h1>` vacío y se publica — porque nada en la cadena sabía que ese campo era obligatorio. Una colección convierte eso en un fallo de compilación con la ruta del archivo dentro. El segundo coste es que esta _API_ ha cambiado dos veces: la forma anterior a la v6 (`src/content/config.ts`, colecciones sin `loader`) fue **eliminada**, no marcada como obsoleta, así que los tutoriales y el código generado que todavía la enseñan producen un proyecto que no compila. Dejar por escrito la forma actual es lo que evita que una base de código se reconstruya contra documentación que ya no aplica.

**Directrices:**

1.  **Un único archivo de configuración, en la raíz de `src/`:**
    - El archivo es `src/content.config.ts` — no `src/content/config.ts`, que era la ubicación anterior a la v6 y ya no funciona
    - Exporta un único objeto `collections` que asocia cada nombre de colección a una llamada a `defineCollection()`
2.  **Cada colección declara un `loader`:**
    - `glob()` de `astro/loaders` para archivos en disco: `glob({ pattern: '**/*.md', base: './src/data/blog' })`
    - `file()` para un único archivo de datos que contiene muchas entradas
    - Un loader propio o de terceros para un _CMS_ o una _API_ — esta es la costura que hace intercambiable el origen del contenido sin tocar las páginas que lo leen
    - No existe un loader implícito. Las colecciones heredadas y la bandera `legacy.collections` se eliminaron en la v6, así que una colección sin loader no es una colección heredada, es una colección rota
3.  **Importa `z` desde `astro/zod`:**
    - `astro/zod` es la reexportación que sigue la versión que _Astro_ distribuye
    - `import { z } from 'astro:content'` y `astro:schema` son rutas obsoletas que todavía aparecen por todo el material antiguo
    - El _Zod_ incluido es la **v4**, cuyos formatos de cadena de nivel superior reemplazaron a los encadenados: `z.email()`, `z.url()`, `z.uuid()` en lugar de `z.string().email()` y compañía
4.  **Las entradas se identifican por `id`:**
    - Las entradas de la Content Layer exponen `id`, generado a partir del nombre del archivo salvo que el frontmatter lo sobrescriba. La propiedad `slug` pertenecía a las colecciones heredadas ya eliminadas
    - Por eso las rutas dinámicas son `[id].astro` y construyen sus params a partir de `post.id`, y todo lo que compone una URL — un feed, una entrada del sitemap, un enlace interno — lee `id`
5.  **Nunca leas los archivos de contenido directamente:**
    - `import.meta.glob()` es la herramienta correcta para recoger módulos en general, y es el reemplazo del `Astro.glob()` eliminado, pero el contenido no es un módulo cualquiera: recurrir a cualquiera de los dos para cargar _Markdown_ salta el esquema, la generación de tipos y el cacheo
    - Leer `src/content/` con `fs` en el frontmatter de una página tiene el mismo problema y además se rompe en cuanto el contenido se mueve
6.  **Recurre a las colecciones en vivo cuando el contenido no puede esperar a una recompilación:**
    - `defineLiveCollection()` en `src/live.config.ts` obtiene los datos en tiempo de solicitud, de modo que las ediciones del _CMS_ aparecen sin volver a desplegar — estable desde la v6
    - Es la herramienta para contenido genuinamente en vivo, no una forma de evitar configurar un build hook

**Incorrecto (la forma heredada eliminada, y contenido leído a mano):**

```ts
// ⚠️ src/content/config.ts — esta ruta dejó de leerse en la v6
import { defineCollection } from 'astro:content';
import { z } from 'astro:content'; // ruta de importación obsoleta

const blog = defineCollection({
  // Mal: sin loader. Las colecciones heredadas se eliminaron, así que esto no compila
  schema: z.object({
    title: z.string(),
    contact: z.string().email(), // encadenado de Zod 3; la v4 quiere z.email()
    pubDate: z.coerce.date(),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[slug].astro
// Mal: salta el esquema por completo — un título ausente es undefined en tiempo de
// ejecución, y `slug` ya no existe en las entradas de colección
const posts = Object.values(import.meta.glob('../../content/blog/*.md', { eager: true }));

export async function getStaticPaths() {
  return posts.map((post) => ({ params: { slug: post.frontmatter.slug } }));
}
---

<h1>{Astro.props.post.frontmatter.title}</h1>
```

**Correcto (la forma actual de la Content Layer, tipada de extremo a extremo):**

```ts
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — los params salen del id de la entrada
import { getCollection, render } from 'astro:content';
import Layout from '@layouts/Article.astro';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);

  return posts.map((post) => ({
    params: { id: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await render(post);
---

<Layout title={post.data.title} description={post.data.description}>
  <h1>{post.data.title}</h1>
  <Content />
</Layout>
```

Referencia: [Content collections](https://docs.astro.build/en/guides/content-collections/)
