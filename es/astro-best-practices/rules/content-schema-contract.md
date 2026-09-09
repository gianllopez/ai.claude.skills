---
title: El esquema es el contrato de publicación
impact: CRITICAL
description: Exige que los campos sin los cuales una página no puede publicarse se declaren y validen en el esquema de la colección, de modo que un valor ausente o mal formado rompa la compilación en lugar de llegar a producción.
tags: content, schema, zod, validation, seo
---

## El esquema es el contrato de publicación

**Impacto (CRITICAL):** Toda página tiene campos sin los cuales no puede ser correcta — un título, una descripción, una fecha de publicación — y hay exactamente dos lugares donde exigirlos: un esquema que rompe la compilación, o una persona que se acuerda. El segundo funciona hasta que un sitio tiene más de un autor, y entonces se degrada en silencio: una entrada se publica sin meta descripción, una fecha se renderiza como `Invalid Date`, un borrador sale a producción porque nadie lo filtró. Ninguno de estos casos lanza un error. Se descubren semanas después en un informe de rastreo, y para entonces la página ya está indexada tal cual. Un esquema convierte cada uno de ellos en un error de compilación que nombra el archivo y el campo, en el momento en que se escribió el contenido, cuando arreglarlo no cuesta nada. Este es el beneficio concreto de la regla anterior: configurar colecciones vale la pena porque el esquema es donde los requisitos de publicación se vuelven mecánicos.

**Directrices:**

1.  **Declara todos los campos que la plantilla lee:**
    - Si un layout, un feed o un componente lee `post.data.x`, entonces `x` pertenece al esquema — un campo opcional que la plantilla no protege es el mismo defecto que uno no declarado
    - Dale a un campo un `.default()` cuando el sitio tenga un valor de reserva razonable, y déjalo obligatorio cuando no lo tenga. `draft: z.boolean().default(false)` es correcto; un título con valor por defecto no
2.  **La línea base de una página guiada por contenido:**
    - `title` y `description` — los dos sin los cuales no se puede componer el head del documento
    - `pubDate`, y `updatedDate` como opcional. Convierte ambos con `z.coerce.date()` para que una fecha mal formada sea un error de compilación en lugar de un `Invalid Date` en la salida renderizada
    - `draft`, con valor por defecto `false` y filtrado en cada lectura, para que el trabajo sin terminar no pueda llegar a una página, un feed o un sitemap
    - Una sobrescritura de canonical, opcional, para los casos genuinos — una URL migrada, una entrada sindicada. Opcional porque una obligatoria invita a poner un valor incorrecto en cada página
    - `tags` y `author` allí donde el sitio los use
3.  **Restringe los valores, no solo los tipos:**
    - `z.string().max(160)` en una descripción atrapa la que se truncará en una página de resultados, en tiempo de compilación
    - `z.enum([...])` para una categoría o un tipo de página, para que una errata no pueda crear una tercera categoría en silencio
    - `.refine()` para una relación que el sistema de tipos no puede expresar — un `updatedDate` anterior a `pubDate` es corrupción de datos, y rechazarlo es una línea
4.  **Nunca falsees la frescura:**
    - `updatedDate` significa que el contenido cambió. Ponerlo en una compilación, un reformateo o una actualización de dependencias lo convierte en ruido, y los consumidores que confían en él (feeds, sitemaps, buscadores) quedan mal informados
    - Esta es una regla sobre lo que el campo significa, y el esquema solo puede exigir que sea una fecha — así que se enuncia aquí para exigirla en la revisión
5.  **Modela las relaciones con `reference()`, no con cadenas libres:**
    - Una entrada relacionada declarada como `reference('blog')` se valida contra la colección, así que una entrada renombrada o eliminada rompe la compilación en lugar de renderizar un enlace muerto
    - Un `z.string()` corriente que guarda el id de una entrada es una clave foránea sin integridad
6.  **Un CMS no elimina el contrato, lo reubica:**
    - Cuando quienes editan publican a través de un _CMS_, los mismos campos obligatorios tienen que existir como campos del _CMS_, y el esquema del loader sigue validando lo que vuelve — una respuesta de _API_ es entrada no confiable como cualquier otra
    - Vale la pena enunciar la frontera explícitamente: quienes editan son dueños del contenido, no del layout. Un _CMS_ que permite a alguien reestructurar una página es un _CMS_ que romperá la página, y el arreglo es el diseño de los campos, no la revisión
    - Esto se sostiene con independencia del proveedor; la elección entre un _CMS_ y colecciones basadas en archivos es una decisión de flujo de trabajo, no técnica

**Incorrecto (un esquema que no tipa nada de lo que el sitio realmente depende):**

```ts
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  // Mal: todo opcional, nada restringido. Una entrada sin descripción compila
  // sin problemas y se publica con una meta etiqueta vacía
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    pubDate: z.string().optional(),
    related: z.array(z.string()).optional(),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — lee campos que el esquema nunca garantizó
const { post } = Astro.props;
---

<meta name="description" content={post.data.description} />
<time>{new Date(post.data.pubDate).toLocaleDateString()}</time>
```

**Correcto (el contrato está declarado, e incumplirlo rompe la compilación):**

```ts
// src/content.config.ts
import { defineCollection, reference } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z
    .object({
      title: z.string().min(1),
      // El truncado en una página de resultados es un error de compilación, no una sorpresa
      description: z.string().max(160),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      // Solo para excepciones genuinas: migraciones, copias sindicadas
      canonicalUrl: z.url().optional(),
      category: z.enum(['engineering', 'product', 'company']),
      // Validado contra la colección: una entrada renombrada rompe la compilación
      related: z.array(reference('blog')).default([]),
      draft: z.boolean().default(false),
    })
    .refine((data) => !data.updatedDate || data.updatedDate >= data.pubDate, {
      message: 'updatedDate cannot precede pubDate',
      path: ['updatedDate'],
    }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — todos los campos que se leen aquí existen con garantía
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  // Los borradores no pueden llegar a una ruta, un feed ni al sitemap
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({ params: { id: post.id }, props: { post } }));
}

const { post } = Astro.props;
---

<meta name="description" content={post.data.description} />
<time datetime={post.data.pubDate.toISOString()}>
  {post.data.pubDate.toLocaleDateString('en', { dateStyle: 'long' })}
</time>
```

Referencia: [Defining a collection schema](https://docs.astro.build/en/guides/content-collections/)
