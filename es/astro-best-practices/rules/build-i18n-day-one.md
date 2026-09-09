---
title: Internacionalización desde el primer día
impact: MEDIUM
description: Configura el enrutado i18n antes de que existan rutas y enlaces, incluso para un sitio de un solo idioma, y construye cada enlace interno con getRelativeLocaleUrl().
tags: i18n, routing, links, configuration
---

## Internacionalización desde el primer día

**Impacto (MEDIUM):** La internacionalización es la única decisión de configuración cuyo coste está casi por completo en cuándo se toma. Configurada al principio son un puñado de líneas y un helper usado para los enlaces internos — el sitio tiene un idioma, el enrutado se comporta exactamente igual que antes, y nada del trabajo diario cambia. Aplicada a posteriori es una reestructuración: `src/pages/` gana un nivel, todas las rutas se mueven, cada enlace interno de cada componente y archivo de contenido hay que encontrarlo y reescribirlo, las colecciones de contenido se reorganizan por idioma, y las redirecciones tienen que preservar las _URLs_ que ya estaban indexadas. El trabajo no es difícil, es amplio y mecánico, y toca archivos que no tenían ningún otro motivo para cambiar. Dado que la versión anticipada es barata incluso para un sitio que nunca añade un segundo idioma, lo predeterminado es configurarla.

**Directrices:**

1.  **Configura `i18n` antes de que existan las rutas:**
    - `defaultLocale`, la lista de `locales` y el comportamiento del enrutado
    - `routing: { prefixDefaultLocale: false }` mantiene el idioma por defecto sin prefijo, de modo que un sitio de un solo idioma tiene exactamente las _URLs_ que habría tenido igualmente — `/blog`, no `/en/blog`
    - Añadir un idioma después es entonces una entrada en una lista y un directorio de contenido, no una migración
2.  **Construye los enlaces internos con el helper, siempre:**
    - `getRelativeLocaleUrl(locale, path)` produce la _URL_ correcta para el idioma actual, así que un enlace escrito una vez sigue funcionando cuando llega un segundo idioma
    - `Astro.currentLocale` es el idioma de la página que se está renderizando
    - Un `href="/blog"` fijo es justo lo que habrá que encontrar y reescribir después, y siempre hay más de los esperados — navegación, pies, tarjetas, llamadas a la acción y enlaces dentro del contenido
3.  **Organiza el contenido por idioma desde el principio:**
    - Un segmento de idioma en la estructura de directorios de la colección (`src/data/blog/en/`, `src/data/blog/es/`) mantiene las entradas direccionables por idioma sin una segunda colección
    - El idioma pasa a formar parte de los params de la ruta, de modo que la ruta dinámica construye ambos idiomas desde un mismo archivo
4.  **Declara en qué idioma está una página:**
    - El atributo `lang` de `<html>` viene del idioma actual, no de una cadena fija en el layout base
    - Un sitio que sirve dos idiomas bajo un único `lang` fijo está describiendo mal todas las páginas del otro
5.  **Cuando un segundo idioma genuinamente no va a llegar nunca:**
    - La configuración sigue costando un bloque y evita la reforma si esa suposición cambia
    - Lo único que no vale la pena construir por anticipado es la maquinaria de traducción — diccionarios, selectores de idioma, salida `hreflang`. Eso llega con el segundo idioma; el enrutado es lo que tiene que existir antes

**Incorrecto (sin configuración, enlaces fijos, idioma afirmado):**

```astro
---
// src/layouts/Base.astro
---

<!-- Mal: fijo. Cada página en un segundo idioma afirmará estar en inglés -->
<html lang="en">
  <body>
    <nav>
      <!-- Mal: rutas absolutas que habrá que reescribir una por una cuando
           aparezca un prefijo de idioma -->
      <a href="/blog">Blog</a>
      <a href="/services">Services</a>
      <a href="/contact">Contact</a>
    </nav>
    <slot />
  </body>
</html>
```

**Correcto (configurado por adelantado, enlaces e idioma derivados):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es'],
    routing: {
      // El idioma por defecto se queda sin prefijo: /blog, no /en/blog
      prefixDefaultLocale: false,
    },
  },
});
```

```astro
---
// src/layouts/Base.astro
import { getRelativeLocaleUrl } from 'astro:i18n';

const locale = Astro.currentLocale ?? 'en';

const links = [
  { path: '/blog', label: 'Blog' },
  { path: '/services', label: 'Services' },
  { path: '/contact', label: 'Contact' },
];
---

<html lang={locale}>
  <body>
    <nav>
      {
        links.map(({ path, label }) => (
          <a href={getRelativeLocaleUrl(locale, path)}>{label}</a>
        ))
      }
    </nav>
    <slot />
  </body>
</html>
```

```astro
---
// src/pages/[...locale]/blog/[id].astro — ambos idiomas desde un archivo de ruta
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);

  return posts.map((post) => {
    const [locale, ...rest] = post.id.split('/');

    return {
      params: { locale: locale === 'en' ? undefined : locale, id: rest.join('/') },
      props: { post },
    };
  });
}
---
```

Referencia: [Internationalization](https://docs.astro.build/en/guides/internationalization/)
