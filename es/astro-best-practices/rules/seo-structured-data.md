---
title: Datos estructurados generados desde el contenido
impact: MEDIUM
description: Exige que el JSON-LD se genere desde el modelo de contenido y describa solo lo que realmente se renderiza en la página, nunca copiado a mano por página ni afirmando cosas sobre contenido que no está ahí.
tags: seo, json-ld, structured-data, schema-org
---

## Datos estructurados generados desde el contenido

**Impacto (MEDIUM):** Los datos estructurados son una afirmación legible por máquinas sobre lo que contiene una página, y su único valor está en ser ciertos. Copiados a mano en cada plantilla dejan de ser ciertos casi de inmediato: el `datePublished` sigue diciendo la fecha de la página de la que se copió, el `author` nombra a alguien que ya se fue, el `headline` no coincide con el `<h1>` porque se editó uno de los dos. Nada de esto aparece en la página renderizada, así que nada lo detecta — la página se ve correcta y se describe a sí misma de forma incorrecta. Generados desde la misma entrada de contenido que la página renderiza, los dos no pueden discrepar, porque hay una única fuente. La otra mitad de la regla es una frontera: un marcado que afirma cosas que la página no muestra — un bloque de FAQ sin FAQ visible, reseñas que nadie escribió — no es una optimización con un riesgo asociado, es una tergiversación, y es de esas cosas que le cuestan a un sitio sus resultados enriquecidos por completo.

**Directrices:**

1.  **Genera desde la entrada, en un único helper:**
    - Una función que recibe la entrada de contenido y devuelve el objeto, renderizado por el layout mediante un único `<script type="application/ld+json">` — la misma forma que la regla de metadatos, por la misma razón
    - Cada campo que emite se lee del esquema. Un valor escrito como literal dentro del helper es un valor que estará mal en alguna página
    - Serializa con `JSON.stringify` y deja que la plantilla lo inserte, en lugar de componer el _JSON_ como una cadena
2.  **Usa los tipos que corresponden a lo que la página realmente es:**
    - `Article` (o `BlogPosting`) para contenido editorial, `BreadcrumbList` para una página dentro de una jerarquía, `Organization` una sola vez para la identidad del negocio, `Service` para una página de servicio real, `Product` para un producto real
    - Una página suele llevar dos: lo que es, más su miga de pan. Más que eso suele ser una página que se describe a sí misma como varias cosas a la vez
3.  **Describe solo lo que se renderiza:**
    - `FAQPage` exige que las preguntas y respuestas sean visibles en la página, no escondidas tras un desplegable que nunca se abre ni presentes únicamente en el marcado
    - Una valoración exige valoraciones reales y recogidas; una dirección de `Organization` exige una dirección real
    - La prueba es si una persona que abre la página puede ver cada afirmación que hace el marcado. Si no puede, el marcado es el defecto
4.  **_URLs_ absolutas, derivadas como el canonical:**
    - `url`, `image`, `@id` y cada referencia son absolutas, construidas a partir de `Astro.site` — una _URL_ relativa en _JSON-LD_ no se resuelve como se resuelve en _HTML_
    - La `url` de la página es su canonical. Si el helper la calcula por separado, las dos divergirán
5.  **Las fechas salen del esquema y siguen su significado:**
    - `datePublished` desde `pubDate`, `dateModified` desde `updatedDate` — y la regla de contenido contra falsear la frescura aplica aquí en primer lugar, porque este es el sitio donde la afirmación se hace explícita
    - Emítelas como cadenas _ISO_; una fecha formateada según la configuración regional no es válida aquí
6.  **Valida la salida, no la plantilla:**
    - Un helper que produce _JSON_ válido puede seguir produciendo datos estructurados inválidos, así que la comprobación se hace contra una página renderizada
    - Hazlo una vez por tipo de página en lugar de una vez por página — el sentido de generarlos es que un tipo correcto sea correcto en todas partes

**Incorrecto (copiado a mano por página, afirmando contenido que la página no tiene):**

```astro
---
// src/pages/blog/introducing-our-api.astro
---

<!-- Mal: copiado de otra entrada. Las fechas, el autor y el titular son los de
     aquella entrada, y nada de esta página los corregirá nunca -->
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Scaling our ingest pipeline",
    "datePublished": "2025-11-04",
    "author": { "@type": "Person", "name": "A. Former-Employee" },
    "image": "/images/og.png",
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.9",
      "reviewCount": "218"
    }
  }
</script>

<!-- ...y no hay ninguna FAQ en ninguna parte de esta página -->
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Is the API free?",
        "acceptedAnswer": { "@type": "Answer", "text": "Yes." }
      }
    ]
  }
</script>
```

**Correcto (derivado de la entrada, describiendo lo que se renderiza):**

```ts
// src/lib/structured-data.ts
import type { CollectionEntry } from 'astro:content';

export function articleSchema(post: CollectionEntry<'blog'>, site: URL) {
  const url = new URL(`/blog/${post.id}`, site).href;

  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.data.title,
    description: post.data.description,
    url,
    mainEntityOfPage: url,
    datePublished: post.data.pubDate.toISOString(),
    // Presente solo cuando el contenido registra realmente una modificación
    ...(post.data.updatedDate && {
      dateModified: post.data.updatedDate.toISOString(),
    }),
    author: { '@type': 'Person', name: post.data.author },
    publisher: { '@type': 'Organization', name: 'Example' },
  };
}
```

```astro
---
// src/layouts/Article.astro
import type { CollectionEntry } from 'astro:content';
import { articleSchema } from '@lib/structured-data';
import Base from '@layouts/Base.astro';

interface Props {
  post: CollectionEntry<'blog'>;
}

const { post } = Astro.props;
const schema = articleSchema(post, Astro.site!);
---

<Base
  title={post.data.title}
  description={post.data.description}
  pageType="article"
>
  <script
    type="application/ld+json"
    set:html={JSON.stringify(schema)}
    is:inline
  />

  <article>
    <h1>{post.data.title}</h1>
    <slot />
  </article>
</Base>
```

Referencia: [Astro.site and absolute URLs](https://docs.astro.build/en/reference/api-reference/)
