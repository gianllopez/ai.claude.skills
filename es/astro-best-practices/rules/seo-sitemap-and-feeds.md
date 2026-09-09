---
title: Higiene del sitemap y los feeds
impact: HIGH
description: Exige que los sitemaps y feeds generados listen solo URLs canónicas e indexables, excluyendo borradores, rutas noindex y orígenes de redirección, con fechas de última modificación que reflejen cambios reales.
tags: seo, sitemap, rss, feeds, indexing
---

## Higiene del sitemap y los feeds

**Impacto (HIGH):** Instalar `@astrojs/sitemap` es la mitad fácil y la mitad que todo el mundo hace; lo que emite por defecto es cada ruta que produjo la compilación. Eso incluye la página de agradecimiento, la ruta de resultados de búsqueda interna, la página de staging con `noindex`, el archivo paginado que nadie quiere indexado y — tras una migración — las _URLs_ antiguas que siguen presentes como orígenes de redirección. Un sitemap es una afirmación de que estas son las páginas que vale la pena rastrear, así que enviar uno que contradice los propios canonicals y directivas de robots del sitio es pedirle a un rastreador que elija entre dos respuestas. Los feeds arrastran el mismo problema con un fallo adicional: un feed construido a partir de la propiedad equivocada de la entrada produce enlaces que dan 404 para todas las personas suscritas a la vez, y los lectores de feeds cachean con la suficiente agresividad como para que la versión rota sobreviva al arreglo.

**Directrices:**

1.  **Filtra el sitemap a lo que realmente debe indexarse:**
    - `@astrojs/sitemap` acepta un predicado `filter`, y no es configuración opcional en ningún sitio real
    - Excluye lo que el propio sitio marca como excluido: rutas con `noindex`, páginas de agradecimiento y confirmación, búsqueda interna, listados filtrados o facetados, rutas de vista previa
    - Excluye los orígenes de redirección. Una _URL_ que responde con 301 pertenece al mapa de redirecciones, nunca al sitemap
    - Los borradores ya quedan excluidos aguas arriba, por el filtro de la colección — un borrador que llega a una ruta es un defecto del modelo de contenido, no del sitemap
2.  **El sitemap coincide con el canonical, o está mal:**
    - Mismo origen, misma convención de barra final, misma _URL_ para la misma página
    - `site` tiene que estar definido para que la integración emita algo, cosa que la regla de metadatos ya exige
3.  **`lastmod` significa que el contenido cambió:**
    - Emítelo desde el propio `updatedDate` del contenido, no desde la marca de tiempo de la compilación — un sitemap sellado por el build afirma que todas las páginas cambiaron en cada despliegue, y un consumidor que se lo cree aprende a ignorarlo
    - Cuando no hay una fecha de modificación fiable, omitir `lastmod` es mejor que fabricar una
4.  **Segmenta los sitios grandes en lugar de emitir una lista plana:**
    - La integración pagina automáticamente al pasar su límite de entradas, y `customPages`, `serialize` y las entradas por sección permiten a un sitio expresar prioridad y frecuencia de cambio allí donde de verdad difieren
    - Un archivo de blog y una página de servicio no cambian al mismo ritmo, y decirlo es justamente el propósito de esos campos
5.  **Los feeds se construyen desde la misma fuente filtrada que las páginas:**
    - `@astrojs/rss` recibe la colección, así que hereda el mismo filtro de borradores y el mismo orden
    - Los enlaces se construyen con `context.site` y el `id` de la entrada — las entradas de la Content Layer no tienen `slug`, y un feed construido sobre `post.slug` emite `/blog/undefined/` en cada elemento
    - Define el `pubDate` del elemento desde el campo de fecha del esquema, no desde el mtime del archivo, que cambia al hacer checkout
6.  **Ambos son artefactos generados, así que se revisan en el origen:**
    - Nada de un sitemap o un feed debería mantenerse a mano; una entrada añadida a mano es un hecho que dejará de ser cierto
    - Tras un lanzamiento, descarga el `/sitemap-index.xml` emitido y confirma que el recuento coincide aproximadamente con el número de páginas indexables — una diferencia de un orden de magnitud es la señal más rápida de que falta un filtro

**Incorrecto (todo lo que emitió la compilación, y un feed construido sobre una propiedad eliminada):**

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Mal: sin filtro. Páginas de agradecimiento, búsqueda interna, rutas de vista
  // previa y las URLs antiguas conservadas para redirecciones se envían todas
  // como canónicas
  integrations: [sitemap()],
});
```

```js
// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // Mal: borradores incluidos, y `post.slug` no existe en las entradas de la
  // Content Layer — cada enlace del feed resuelve a /blog/undefined/
  const posts = await getCollection('blog');

  return rss({
    title: 'Example Blog',
    description: 'Notes from the team',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      link: `/blog/${post.slug}/`,
    })),
  });
}
```

**Correcto (filtrado a URLs indexables, feed construido a partir de `id`):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const EXCLUDED = ['/thank-you', '/search', '/preview'];

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',
  integrations: [
    sitemap({
      // Solo las URLs canónicas e indexables llegan al sitemap
      filter: (page) => {
        const { pathname } = new URL(page);
        return !EXCLUDED.some((prefix) => pathname.startsWith(prefix));
      },
    }),
  ],
});
```

```js
// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // El mismo filtro que usan las rutas, para que el feed no pueda contener lo que
  // el sitio no contiene
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );

  return rss({
    title: 'Example Blog',
    description: 'Notes from the team',
    site: context.site,
    items: sorted.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      // `id`, y la convención de barra final del sitio
      link: `/blog/${post.id}`,
    })),
  });
}
```

Referencia: [@astrojs/sitemap](https://docs.astro.build/en/guides/integrations-guide/sitemap/)
