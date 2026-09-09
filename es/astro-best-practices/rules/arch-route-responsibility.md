---
title: Responsabilidad de las rutas, layouts y slots
impact: HIGH
description: Mantiene los archivos de ruta limitados a reunir datos y componer componentes, con la estructura repetida en manos de los layouts y expuesta mediante slots en lugar de repetirse página por página.
tags: architecture, routing, layouts, slots, structure
---

## Responsabilidad de las rutas, layouts y slots

**Impacto (HIGH):** El trabajo de un archivo de ruta es responder a una pregunta — qué hay en esta página — y en el momento en que además contiene el marcado de la cabecera, las etiquetas de metadatos, el pie y tres secciones incrustadas, esa respuesta queda enterrada en un archivo que nadie puede recorrer de un vistazo. El coste no es estético. La estructura repetida implica que un cambio en el marco del sitio es un cambio en cada ruta que lo copió, así que la cabecera se actualiza en once archivos y se olvida en el duodécimo, y el olvidado lo descubre quien lee. Lo mismo aplica a los metadatos: el marco de la página es donde viven el `<title>` y los canonicals, y una ruta que compone su propio head es una ruta que puede divergir de las reglas del sitio. Los layouts existen precisamente para que la parte repetida tenga una única definición y la parte que varía llegue a través de slots.

**Directrices:**

1.  **Un archivo de ruta compone; no contiene:**
    - Obtén o lee los datos de la página en el frontmatter, elige un layout, pasa props, compón componentes
    - El marcado de una sección escrito en línea dentro de una ruta es un componente que todavía no se ha extraído — se queda en línea solo mientras sea genuinamente de un solo uso, cosa que cubre la regla de componentes
    - Una ruta que ha crecido más allá de aproximadamente una pantalla de marcado suele estar guardando algo que pertenece a otro sitio
2.  **Los layouts son dueños de todo lo que se repite:**
    - El esqueleto del documento, el componente de metadatos, la navegación global, las migas de pan, el pie, los enlaces de salto, el hook de datos estructurados
    - Los layouts se componen: un layout `Base` que contiene el documento, y un layout `Article` que lo envuelve con las partes que comparten todos los artículos. Anidarlos es mejor que duplicar cualquiera de los dos
    - Los valores por defecto viven en el layout, de modo que una página a la que no le importa obtiene un valor correcto sin declarar ninguno
3.  **Los slots son la interfaz entre ambos:**
    - El slot por defecto para el contenido de la página, y slots con nombre para el marco que una página puede rellenar — un aside, un hero, un conjunto de acciones en la cabecera
    - `<slot name="x" />` con contenido de reserva dentro significa que una página que no aporta nada se sigue renderizando correctamente
    - Un layout que recibe marcado como prop en lugar de como slot está rodeando el mecanismo diseñado para eso
4.  **Las convenciones de directorios cargan significado, así que consérvalas:**
    - `src/pages/` es enrutado y nada más — cada archivo dentro es una _URL_
    - `src/layouts/` para el marco de página, `src/components/` para todo lo componible, `src/content.config.ts` junto al contenido que describe, `src/lib/` (o `src/utils/`) para la lógica que no es un componente, `src/styles/` para las hojas de estilo globales
    - Agrupa las rutas por sección (`src/pages/blog/`, `src/pages/services/`) para que un listado de directorio describa la forma del sitio
5.  **Los datos van al principio de la ruta, no repartidos por ella:**
    - Todo lo que la página necesita se resuelve en el frontmatter, de modo que quien lee conoce las entradas de la página sin recorrer su marcado
    - `getStaticPaths()` devuelve tanto `params` como `props`, así que una ruta dinámica pasa su entrada hacia abajo en lugar de volver a obtenerla más adelante
6.  **La prueba:**
    - Añadir una página nueva de un tipo que ya existe debería requerir escribir únicamente lo que la hace distinta. Si requiere copiar el marco, los metadatos o la navegación, el layout no está haciendo su trabajo

**Incorrecto (una ruta que contiene el documento entero, y metadatos compuestos página por página):**

```astro
---
// src/pages/services/migration.astro
const testimonials = await getTestimonials();
---

<!-- Mal: el esqueleto del documento, la navegación, los metadatos y cada sección
     en línea. Cambiar la cabecera significa editar este archivo y todos sus hermanos -->
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Migration services | Example</title>
    <meta name="description" content="We help teams move their site." />
    <link rel="canonical" href="https://example.com/services/migration" />
  </head>
  <body>
    <header class="site-header">
      <a href="/">Example</a>
      <nav>
        <a href="/blog">Blog</a>
        <a href="/services">Services</a>
      </nav>
    </header>

    <main>
      <section class="hero">
        <h1>Website migration</h1>
        <p>Move without losing what you have built.</p>
      </section>

      <section class="testimonials">
        {
          testimonials.map((t) => (
            <figure>
              <blockquote>{t.quote}</blockquote>
              <figcaption>{t.author}</figcaption>
            </figure>
          ))
        }
      </section>
    </main>

    <footer class="site-footer">© Example</footer>
  </body>
</html>
```

**Correcto (el layout es dueño del marco, la ruta compone la página):**

```astro
---
// src/layouts/Base.astro — el esqueleto, una sola vez
import SeoHead from '@components/SeoHead.astro';
import SiteHeader from '@components/SiteHeader.astro';
import SiteFooter from '@components/SiteFooter.astro';

interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
}

const props = Astro.props;
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <SeoHead {...props} />
    <slot name="head" />
  </head>
  <body>
    <SiteHeader />
    <main>
      <slot />
    </main>
    <SiteFooter />
  </body>
</html>
```

```astro
---
// src/pages/services/migration.astro — solo lo que hace distinta a esta página
import Base from '@layouts/Base.astro';
import Hero from '@components/Hero.astro';
import TestimonialList from '@components/TestimonialList.astro';

const testimonials = await getTestimonials();
---

<Base
  title="Website migration"
  description="Move without losing what you have built."
  pageType="service"
>
  <Hero
    title="Website migration"
    subtitle="Move without losing what you have built."
  />
  <TestimonialList items={testimonials} />
</Base>
```

Referencia: [Project structure](https://docs.astro.build/en/basics/project-structure/)
