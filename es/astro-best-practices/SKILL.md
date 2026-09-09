---
name: astro-best-practices
description: Estándares para sitios web Astro 7 en producción — salida estática por defecto, componentes .astro antes que componentes de framework, directivas de hidratación acordes a la posición del componente, contenido tipado mediante la Content Layer API, SEO generado desde el esquema de contenido, las APIs integradas de imagen, tipografía, prefetch y transiciones de vista, tematización con TailwindCSS v4 en CSS, y la configuración de versión, entorno y CSP que un proyecto necesita. Úsala al escribir o revisar archivos .astro, astro.config.mjs, colecciones de contenido y sus esquemas, directivas client:*, la estructura de rutas y layouts, o la configuración de SEO, recursos y despliegue de un proyecto. En un proyecto que usa islas de React, react-core-best-practices se carga junto a esta skill y es dueña de todo lo que ocurre dentro de esos componentes.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# Buenas prácticas de Astro

Estándares para construir sitios web de producción con _Astro_, donde casi toda decisión que importa se reduce a una pregunta: ¿cuánto de esta página tiene que llegar al navegador como _JavaScript_? _Astro_ la responde bien por defecto — renderiza _HTML_ en tiempo de compilación y no envía nada más hasta que se lo pides — así que la mayoría de los defectos en una base de código _Astro_ no son cosas que hiciera el framework, son valores por defecto de los que se salió sin un motivo.

Esa forma es la que codifican estas reglas. Salida estática salvo que una página demuestre que necesita el servidor. Un componente `.astro` salvo que la interactividad demuestre que necesita un framework. `client:visible` salvo que la posición demuestre que necesita `client:load`. Una colección tipada salvo que el contenido demuestre que necesita un _CMS_. En cada pareja la primera opción es gratis y la segunda se paga, y la regla no es "nunca pagues" — es que el pago sea una decisión que alguien tomó, visible en el diff, en lugar de un valor por defecto que nadie cuestionó.

Cada regla nombra un defecto lo bastante concreto como para señalarlo en un diff — un `<img>` donde aplica `<Image />`, un `client:load` en un componente por debajo del pliegue, una colección sin `loader`, dos convenciones de barra final en un mismo sitio — y muestra la forma correcta a su lado. Eso es lo que hace que la misma regla sirva en ambas direcciones: el bloque **Correcto** es lo que hay que escribir, y el defecto es lo que hay que buscar.

**Versión de referencia: Astro 7.** El framework avanza rápido y sus versiones mayores recientes eliminaron _APIs_ reales — `Astro.glob()`, las colecciones de contenido heredadas, `<ViewTransitions />`, `@astrojs/db`. Cada regla que nombra una clave de configuración, una ruta de importación o un componente declara la versión a la que pertenece, de modo que la guía se degrada hasta ser una referencia desactualizada en lugar de enseñar en silencio una _API_ eliminada. Cuando la intención de una regla sobrevive a su _API_, se enuncia primero la intención y después la _API_.

**Alcance.** El framework y lo que emite. En un proyecto que renderiza islas de _React_, `react-core-best-practices` se carga junto a esta skill y es dueña de lo que ocurre dentro de esos componentes — efectos, estado, la capa de consultas, la composición y el tipado; esta skill es dueña solo de la frontera: si la isla debe existir y cómo se hidrata. La dirección de diseño visual queda deliberadamente fuera de alcance — no es verificable contra un diff — y también lo queda la auditoría de accesibilidad, en coherencia con la decisión que ya toma `react-best-practices`: las reglas semánticas y estructurales de aquí se justifican por legibilidad para máquinas y mantenibilidad.

## Cuándo aplicarla

Consulta estas guías cuando:

- Decidas si una página se renderiza en tiempo de compilación o bajo demanda, o añadas un adaptador
- Escribas un componente y elijas entre `.astro` y un componente de framework
- Añadas una directiva `client:*`, o revises una que ya está ahí
- Definas una colección de contenido, su `loader` o su esquema
- Añadas metadatos, canonicals, un sitemap, un feed, redirecciones o datos estructurados
- Coloques una imagen, una tipografía, una incrustación o una etiqueta de terceros en una página
- Decidas dónde vive un archivo de ruta, layout o componente, o qué puede contener un archivo de ruta
- Configures _TailwindCSS_ en un proyecto _Astro_, o escribas estilos de componente
- Toques `astro.config.mjs` — i18n, registro, variables de entorno, _CSP_, destino de despliegue

## Categorías de reglas por prioridad

| Prioridad | Categoría                   | Impacto máximo | Prefijo    |
| :-------- | :-------------------------- | :------------- | :--------- |
| 1         | Renderizado e hidratación   | CRITICAL       | `isl-`     |
| 2         | Modelo de contenido         | CRITICAL       | `content-` |
| 3         | Sistema de SEO              | CRITICAL       | `seo-`     |
| 4         | Recursos y rendimiento      | HIGH           | `perf-`    |
| 5         | Estructura del proyecto     | HIGH           | `arch-`    |
| 6         | Estilos                     | HIGH           | `style-`   |
| 7         | Compilación y configuración | HIGH           | `build-`   |

La prioridad ordena dónde mirar primero; el impacto máximo es el de la regla más fuerte de la sección, y coincide con la tabla de contenidos de `AGENTS.md`. Discrepan a propósito — una sección puede contener una regla bloqueante y varias que solo llegan a producir sugerencias.

## Referencia rápida

### 1. Renderizado e hidratación (CRITICAL)

- `isl-static-by-default` - `output: 'static'` declarado explícitamente; el renderizado bajo demanda se adopta ruta por ruta, nunca de forma global por accidente
- `isl-astro-components-first` - `.astro` hasta que la interactividad demuestre lo contrario; un componente de framework es una decisión, no una costumbre
- `isl-hydration-directives` - La directiva corresponde a la posición del componente; la frontera de la isla envuelve lo que es interactivo, no la sección que lo rodea

### 2. Modelo de contenido (CRITICAL)

- `content-collections-required` - Content Layer API: `src/content.config.ts`, cada colección con un `loader`, entradas identificadas por `id`
- `content-schema-contract` - El esquema es donde un campo obligatorio se convierte en un fallo de compilación; validación en tiempo de compilación, no una etiqueta ausente en producción
- `content-authoring-format` - Markdown para texto, MDX solo cuando hacen falta componentes; `<Code />` para código dinámico en tiempo de compilación; el procesador configurado para la v7

### 3. Sistema de SEO (CRITICAL)

- `seo-site-and-canonical` - `site` siempre definido; los canonicals y los metadatos salen de helpers compartidos, nunca se componen a mano página por página
- `seo-url-hygiene` - Una única convención de barra final; las URLs antiguas redirigidas antes del lanzamiento y los enlaces internos apuntando a destinos finales
- `seo-sitemap-and-feeds` - Solo URLs canónicas e indexables; borradores, vistas previas y orígenes de redirección excluidos; fechas de última modificación nunca falseadas
- `seo-structured-data` - JSON-LD generado desde el modelo de contenido, describiendo lo que realmente hay en la página

### 4. Recursos y rendimiento (HIGH)

- `perf-images` - `<Image />` / `<Picture />` en lugar de `<img>` en crudo; dimensiones explícitas, tratamiento deliberado del LCP, carga diferida por debajo del pliegue
- `perf-fonts` - La Fonts API integrada autoaloja, subconjunta y precarga; sin CDN de fuentes de terceros
- `perf-third-party-scripts` - Sin etiquetas globales por defecto; incrustaciones acotadas a las páginas que las necesitan
- `perf-navigation` - `prefetch` y `<ClientRouter />` integrados; transiciones expresadas en CSS en lugar de un runtime de animación en JavaScript

### 5. Estructura del proyecto (HIGH)

- `arch-route-responsibility` - Los archivos de ruta componen; los layouts son dueños de la estructura repetida y la exponen mediante slots
- `arch-component-reuse` - Extrae lo que se repite, mantén local lo genuinamente único; ni copiar y pegar ni abstraer por abstraer
- `arch-path-aliases` - Alias declarados en `tsconfig.json`, no cadenas `../../../`
- `arch-markup-discipline` - Bajo el compilador de la v7 las etiquetas sin cerrar son errores de compilación y los espacios se comprimen; la corrección del marcado es ahora un asunto de compilación

### 6. Estilos (HIGH)

- `style-tailwind-v4-setup` - `@tailwindcss/vite`, nunca el obsoleto `@astrojs/tailwind`; tokens declarados en `@theme`, conectados a la variable de la Fonts API
- `style-scoped-css` - Los estilos de componente se quedan con ámbito; `is:global` es una vía de escape que nombra su motivo

### 7. Compilación y configuración (HIGH)

- `build-i18n-day-one` - Configurada antes de que existan las rutas; enlaces internos construidos con `getRelativeLocaleUrl()`
- `build-logging` - `Astro.logger` y el campo estable `logger` de nivel superior antes que `console.log`
- `build-env-and-csp` - `astro:env` tipa el entorno y mantiene los secretos en el servidor; la CSP se configura, no se omite
- `build-deployment-target` - Salida estática a un CDN de borde; el adaptador, el modo de salida y el mínimo del toolchain declarados explícitamente

## Cómo usarla

Lee los archivos de regla individuales para explicaciones detalladas y ejemplos de código:

```plaintext
rules/*.md
```

## Documento compilado completo

Para la guía completa con todas las reglas expandidas: `AGENTS.md` (generado — ver `README.md`).
