---
title: Componentes reutilizables y componentes específicos de página
impact: MEDIUM
description: Extrae un componente cuando un patrón realmente se repite y mantiene locales las secciones genuinamente únicas, rechazando tanto el copiar y pegar entre rutas como la abstracción construida antes de que exista un segundo consumidor.
tags: architecture, components, composition, reuse
---

## Componentes reutilizables y componentes específicos de página

**Impacto (MEDIUM):** Esta regla tiene dos modos de fallo que tiran en direcciones opuestas, y por eso enunciar solo uno de ellos empeora una base de código. El copiar y pegar es el conocido: un patrón de tarjeta vive en seis rutas, un cambio de diseño aterriza en cinco de ellas, y el sitio queda sutilmente inconsistente de una forma que ningún archivo por separado revela. El menos comentado es la corrección que se pasa de frenada — un componente `Section` con once props y cuatro booleanos, construido para que el hero de una landing page pudiera compartir código con un bloque de precios con el que no tiene nada en común. Ese componente es más difícil de leer que la duplicación que reemplazó, y cada página futura paga un impuesto a una generalización que se inventó en lugar de observarse. La distinción que resuelve ambos casos no es "cuántas veces ha aparecido esto" sino si las instancias son la misma cosa o simplemente se parecen hoy.

**Directrices:**

1.  **Extrae lo que se repite, cuando se repite:**
    - Botones, tarjetas, rejillas de tarjetas, llamadas a la acción, bloques de FAQ, listas de contenido relacionado, secciones de prueba social y testimonios, campos de formulario — los patrones que un sitio usa en todas partes
    - Extrae lo bastante pronto como para proteger la consistencia: la segunda aparición suele ser el momento correcto, porque es cuando se hace posible ver qué varía realmente
    - El componente extraído recibe la variación como props, y las props son las cosas que de verdad difieren — no todos los atributos, por si acaso
2.  **Mantén locales las secciones genuinamente únicas:**
    - El hero de una landing page de campaña, una tabla de precios que existe una sola vez, una sección construida alrededor de un argumento concreto — estas pertenecen a su página
    - `src/components/<ruta>/` o un componente junto a la ruta mantiene una sección de un solo uso fuera del espacio de nombres compartido, donde su presencia daría a entender que es reutilizable
    - Ser largo no es razón para extraer. Repetirse sí lo es
3.  **La prueba es la mismidad, no el parecido:**
    - Dos bloques que se parecen pero cambian por razones distintas son dos componentes. Fusionarlos produce un componente que hay que editar con cuidado en ambas direcciones para siempre
    - Dos bloques que siempre se cambiarían juntos son un componente, aunque hoy se rendericen de forma ligeramente distinta
4.  **Composición antes que configuración:**
    - Cuando un componente empieza a acumular booleanos (`showIcon`, `isCompact`, `variantLarge`), los slots suelen ser la respuesta: deja que quien llama pase la parte que difiere en lugar de describirla
    - Un componente con más configuración que marcado se ha convertido en un pequeño framework, y leerlo cuesta más que la duplicación que evita
5.  **El objetivo es la velocidad de publicación, no la pureza arquitectónica:**
    - La medida es si se puede crear una página nueva de un tipo existente sin duplicar layout, metadatos o lógica de contenido
    - La abstracción que no sirve a esa medida no se está pagando a sí misma, y la abstracción construida antes de que exista un segundo consumidor no puede saber qué abstraer

**Incorrecto (la misma tarjeta copiada entre rutas, y una sección sobregeneralizada hasta convertirse en un cuadro de mandos):**

```astro
---
// src/pages/blog/index.astro — y otra vez, casi idéntica, en /services y /case-studies
---

<article class="rounded-lg border p-4">
  <h3 class="text-lg font-semibold">{post.data.title}</h3>
  <p class="text-sm text-neutral-600">{post.data.description}</p>
  <a href={`/blog/${post.id}`}>Read more</a>
</article>
```

```astro
---
// src/components/Section.astro
// Mal: construido para unificar un hero, un bloque de precios y una franja de
// testimonios, que son tres cosas distintas que resultaban ser rectángulos
interface Props {
  variant: 'hero' | 'pricing' | 'testimonial' | 'cta' | 'feature';
  title?: string;
  subtitle?: string;
  showIcon?: boolean;
  isCompact?: boolean;
  isCentered?: boolean;
  hasBackground?: boolean;
  columns?: 1 | 2 | 3 | 4;
  items?: unknown[];
  ctaLabel?: string;
  ctaHref?: string;
}
---
```

**Correcto (un componente para el patrón repetido, slots para lo que varía, lo único se queda local):**

```astro
---
// src/components/ContentCard.astro — el patrón que sí se repite
interface Props {
  title: string;
  description: string;
  href: string;
}

const { title, description, href } = Astro.props;
---

<article class="rounded-lg border p-4">
  <h3 class="text-lg font-semibold">{title}</h3>
  <p class="text-sm text-neutral-600">{description}</p>
  <!-- Lo que varía se pasa, no se describe con una bandera -->
  <slot name="meta" />
  <a href={href}>Read more</a>
</article>
```

```astro
---
// src/pages/blog/index.astro
import ContentCard from '@components/ContentCard.astro';
---

{
  posts.map((post) => (
    <ContentCard
      title={post.data.title}
      description={post.data.description}
      href={`/blog/${post.id}`}
    >
      <time slot="meta" datetime={post.data.pubDate.toISOString()}>
        {post.data.pubDate.toLocaleDateString('en', { dateStyle: 'medium' })}
      </time>
    </ContentCard>
  ))
}
```

```astro
---
// src/components/campaign/SpringLaunchHero.astro
// Esto existe una vez, para una página, y lo declara por dónde vive
---

<section class="campaign-hero">
  <h1>Spring launch</h1>
  <slot />
</section>
```

Referencia: [Astro components](https://docs.astro.build/en/basics/astro-components/)
