---
title: Higiene de URLs, redirecciones y migración
impact: HIGH
description: Exige una única convención de barra final en todo el sitio, y que las URLs antiguas se mapeen y redirijan antes del lanzamiento, con los enlaces internos actualizados a sus destinos finales.
tags: seo, urls, redirects, migration, routing
---

## Higiene de URLs, redirecciones y migración

**Impacto (HIGH):** Una _URL_ es un identificador, y un sitio que sirve la misma página bajo dos identificadores le ha dicho a los buscadores que tiene dos páginas. `/blog` y `/blog/` es el caso habitual, y a ningún buscador le importa qué convención elija un sitio — solo le importa que elija una. Las convenciones mezcladas llegan por accidente: `trailingSlash` se queda en su valor por defecto mientras los enlaces se escriben de ambas formas, así que los enlaces internos, los canonicals y el sitemap se contradicen entre sí y con lo que el hosting realmente sirve. La migración es el mismo defecto a escala. Un relanzamiento que cambia la estructura de _URLs_ sin un mapa de redirecciones no pierde posicionamiento poco a poco; deja caer todas las _URLs_ indexadas a un 404 de golpe, y las páginas que tardaron años en ganarse su posición vuelven a empezar. Ambos casos son baratos de prevenir antes del lanzamiento y caros de reparar después.

**Directrices:**

1.  **Elige `trailingSlash` explícitamente y haz que todo lo siga:**
    - `trailingSlash: 'always'` o `'never'` en `astro.config.mjs` — el valor importa mucho menos que el hecho de declararlo
    - Los enlaces internos, los canonicals, las entradas del sitemap y los enlaces de los feeds tienen que coincidir con él. Un canonical derivado (ver la regla de metadatos) hereda esto gratis; los enlaces escritos a mano no
    - Confirma que el hosting está de acuerdo: algunas plataformas reescriben o redirigen una forma a la otra, y una configuración que discrepa del hosting produce una redirección en cada navegación interna
2.  **Los slugs son parte del modelo de contenido, no una ocurrencia tardía:**
    - Minúsculas, con guiones, sin fechas ni ids salvo que aporten significado, sin palabras vacías añadidas para alargar
    - El `id` de la entrada produce el slug por defecto; cuando una _URL_ tiene que diferir del nombre del archivo, la sobrescritura va en el frontmatter para que sea revisable
    - Un cambio de slug es un cambio de _URL_, lo que significa que es una redirección — no un renombrado
3.  **Una migración empieza con un inventario, antes de cualquier código:**
    - Exporta la lista de _URLs_ existentes desde la analítica, el sitemap antiguo y Search Console — no desde el código antiguo, que no sabe qué _URLs_ están realmente indexadas
    - Mapea cada una a su nuevo destino, y conserva la ruta cuando no haya razón para cambiarla. La reestructuración del tipo "ya que estamos" es la forma en que las migraciones pierden páginas
    - Las _URLs_ sin sucesora reciben una redirección al equivalente genuino más cercano, o se dejan dar 404 deliberadamente — una redirección masiva de todo a la portada se trata como un soft 404 y no ayuda en nada
4.  **Declara las redirecciones en la configuración, no en el marcado:**
    - `redirects` en `astro.config.mjs` mantiene el mapa en un único lugar revisable y emite lo correcto para la plataforma de destino
    - Una etiqueta meta-refresh o un `location.replace()` en el cliente no es una redirección: cuesta una carga de página, y no transmite la señal que sí transmite un 301
    - Usa un estado permanente para un traslado permanente; una redirección temporal en un cambio permanente mantiene viva la _URL_ antigua indefinidamente
5.  **Actualiza los enlaces internos al destino final:**
    - Los enlaces que apuntan a una redirección siguen funcionando, y por eso sobreviven — cada uno es una ida y vuelta desperdiciada y una señal diluida
    - Después de una migración, el conjunto de enlaces internos es parte de lo que se actualiza, no algo que las redirecciones justifiquen
6.  **Verifica después del despliegue, no antes:**
    - El comportamiento de las redirecciones depende tanto del hosting como de la configuración, así que la comprobación que importa se ejecuta contra producción
    - Revisa por muestreo las _URLs_ antiguas de más tráfico buscando una redirección de un solo salto a un 200, y vigila las cadenas — una redirección a otra redirección es una configuración que se ha editado dos veces y reconciliado cero

**Incorrecto (convenciones mezcladas, y un relanzamiento sin mapa):**

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Mal: sin declarar. Los enlaces se escriben de ambas formas y nada los reconcilia
});
```

```astro
<!-- Mal: tres convenciones en una misma navegación, y una redirección en el cliente
     haciendo las veces de la estructura de URLs antigua -->
<a href="/blog">Blog</a>
<a href="/services/">Services</a>
<a href="https://example.com/about">About</a>

<script>
  if (location.pathname.startsWith('/old-blog')) {
    location.replace('/blog');
  }
</script>
```

**Correcto (una convención, redirecciones declaradas, enlaces apuntando a destinos finales):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',

  // El mapa de migración, revisable en un solo lugar. Traslados permanentes,
  // estado permanente
  redirects: {
    '/old-blog/[...slug]': {
      status: 301,
      destination: '/blog/[...slug]',
    },
    '/services/website-migration-2024': {
      status: 301,
      destination: '/services/migration',
    },
  },
});
```

```astro
---
// src/components/SiteNav.astro — una convención, enlaces a destinos finales
const links = [
  { href: '/blog', label: 'Blog' },
  { href: '/services', label: 'Services' },
  { href: '/about', label: 'About' },
];
---

<nav>
  {links.map(({ href, label }) => <a href={href}>{label}</a>)}
</nav>
```

Referencia: [Configured redirects](https://docs.astro.build/en/guides/routing/)
