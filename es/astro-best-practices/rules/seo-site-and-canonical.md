---
title: URL del sitio, metadatos y canonicals
impact: CRITICAL
description: Exige que la opción site esté definida y que el título, la descripción, el canonical y el comportamiento de robots de cada página los produzca un único componente compartido en lugar de componerse página por página.
tags: seo, metadata, canonical, head, configuration
---

## URL del sitio, metadatos y canonicals

**Impacto (CRITICAL):** `site` es una línea de configuración de la que dependen en silencio varias cosas sin relación entre sí: `Astro.site`, cada _URL_ absoluta construida a partir de ella, la integración de sitemap (que se niega a ejecutarse sin ella) y las etiquetas canonical. Si se omite, ninguna falla de forma ruidosa — el sitemap simplemente no está y los canonicals son relativos o faltan, que es exactamente el modo de fallo que nadie nota hasta que llega un informe de rastreo. El defecto mayor son los metadatos compuestos a mano en cada página. Empieza como tres etiquetas copiadas entre plantillas y acaba siendo un sitio donde un tercio de las páginas comparte una misma descripción, dos páginas reclaman el mismo canonical, y una ruta duplicada para una campaña compite con su propio original. Los metadatos son contenido generado — derivado del modelo de contenido por un único componente — y en cuanto se escriben a mano página por página empiezan a divergir.

**Directrices:**

1.  **Define `site` en `astro.config.mjs`, siempre:**
    - Es el origen de producción, sin barra final: `site: 'https://example.com'`
    - Sin él, `Astro.site` es `undefined`, las _URL_ absolutas se vuelven relativas en silencio, y `@astrojs/sitemap` no emite nada
2.  **Un único componente de head es dueño de los metadatos de todo el sitio:**
    - Recibe `title`, `description` y las sobrescrituras opcionales como props, y todos los layouts lo renderizan — no hay un segundo sitio donde se escriba un `<title>`
    - Los valores por defecto viven en él: el sufijo con el nombre del sitio, la imagen social de reserva, el valor de `robots` por defecto
    - Las reglas por tipo de página también viven ahí. El patrón de título de una entrada de blog, el de una página de servicio, el de la portada — expresados una vez como función del tipo de página, no reescritos archivo por archivo
3.  **Deriva el canonical, no lo escribas:**
    - `new URL(Astro.url.pathname, Astro.site)` es el canonical de casi cualquier página, y al ser derivado no puede contradecir la ruta en la que vive
    - Acepta una prop de sobrescritura para las excepciones genuinas — una _URL_ migrada, una copia sindicada, una vista filtrada que debería apuntar a su padre sin filtrar — y haz que venga del esquema de contenido, para que la excepción sea un dato y sea revisable
    - Un canonical escrito a mano es, con diferencia, la forma más común de que dos páginas acaben afirmando ser la misma página
4.  **Haz que `noindex` sea una decisión con un motivo:**
    - Páginas de agradecimiento, listados filtrados o facetados, resultados de búsqueda interna, rutas de staging, páginas paginadas más allá de la primera cuando el sitio no las quiere indexadas
    - Va en ese mismo componente como una prop, para que una página con `noindex` se vea como tal en el punto de llamada en lugar de quedar escondida en una meta etiqueta suelta
    - El defecto inverso es real y peor: un `noindex` olvidado de un despliegue de staging en una página que debería posicionar
5.  **Las etiquetas de Open Graph y sociales salen de la misma fuente que las propias de la página:**
    - Que `og:title` repita el título de la página y `og:description` repita la descripción es correcto — lo que no es correcto es un segundo par escrito a mano que diverge del primero
    - `og:url` es el canonical. Si pueden discrepar, tarde o temprano discreparán
6.  **Los títulos y las descripciones son contenido, así que pertenecen al esquema:**
    - Las reglas de contenido ya los exigen; esta regla es la que los consume
    - Un tipo de página sin una entrada de contenido detrás — una landing page escrita como ruta — sigue pasando props explícitas, y sigue haciéndolo por el mismo componente

**Incorrecto (`site` ausente, metadatos escritos página por página, canonical a mano):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // Mal: sin `site`. Astro.site es undefined y el sitemap no emite nada
  integrations: [sitemap()],
});
```

```astro
---
// src/pages/services/migration.astro
---

<html lang="en">
  <head>
    <!-- Mal: tres etiquetas copiadas de otra página, una de ellas sin actualizar.
         El canonical está escrito a mano y apunta a la página de la que se copió -->
    <title>Migration services</title>
    <meta name="description" content="We help teams move their site." />
    <link rel="canonical" href="https://example.com/services/redesign" />
    <meta property="og:title" content="Website migration | Example" />
  </head>
  <body>
    <slot />
  </body>
</html>
```

**Correcto (`site` definido, un único componente de head, canonical derivado):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',
  integrations: [sitemap()],
});
```

```astro
---
// src/components/SeoHead.astro — el único lugar donde se escriben metadatos
interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
  canonicalOverride?: string;
  noindex?: boolean;
  image?: string;
}

const {
  title,
  description,
  pageType = 'service',
  canonicalOverride,
  noindex = false,
  image = '/og-default.png',
} = Astro.props;

const SITE_NAME = 'Example';

// Reglas de título por tipo de página, declaradas una sola vez
const fullTitle = pageType === 'home' ? SITE_NAME : `${title} | ${SITE_NAME}`;

// Derivado, así que no puede contradecir la ruta en la que se renderiza
const canonical = canonicalOverride ?? new URL(Astro.url.pathname, Astro.site);
const socialImage = new URL(image, Astro.site);
---

<title>{fullTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonical} />
{noindex && <meta name="robots" content="noindex, nofollow" />}

<meta property="og:title" content={fullTitle} />
<meta property="og:description" content={description} />
<meta property="og:url" content={canonical} />
<meta property="og:image" content={socialImage} />
<meta name="twitter:card" content="summary_large_image" />
```

```astro
---
// src/layouts/Base.astro — todas las páginas llegan a los metadatos por aquí
import SeoHead from '@components/SeoHead.astro';

interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
  canonicalOverride?: string;
  noindex?: boolean;
}

const props = Astro.props;
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <SeoHead {...props} />
  </head>
  <body>
    <slot />
  </body>
</html>
```

Referencia: [Configuration reference: site](https://docs.astro.build/en/reference/configuration-reference/)
