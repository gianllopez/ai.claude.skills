---
title: Secciones de reglas
description: Índice de las buenas prácticas de Astro 7; lo que ocurre dentro de una isla de React pertenece a react-core-best-practices, que un proyecto que renderiza islas carga junto a esta.
---

## Renderizado e hidratación

- **Salida:** [Salida estática por defecto](./isl-static-by-default.md)
- **Componentes:** [Componentes .astro antes que componentes de framework](./isl-astro-components-first.md)
- **Hidratación:** [Directivas de hidratación y fronteras de isla](./isl-hydration-directives.md)

## Modelo de contenido

- **Colecciones:** [Colecciones de contenido a través de la Content Layer API](./content-collections-required.md)
- **Esquema:** [El esquema es el contrato de publicación](./content-schema-contract.md)
- **Autoría:** [Markdown, MDX y el componente Code](./content-authoring-format.md)

## Sistema de SEO

- **Identidad:** [URL del sitio, metadatos y canonicals](./seo-site-and-canonical.md)
- **URLs:** [Higiene de URLs, redirecciones y migración](./seo-url-hygiene.md)
- **Descubrimiento:** [Higiene del sitemap y los feeds](./seo-sitemap-and-feeds.md)
- **Esquema:** [Datos estructurados generados desde el contenido](./seo-structured-data.md)

## Recursos y rendimiento

- **Imágenes:** [Manejo de imágenes y estabilidad del layout](./perf-images.md)
- **Tipografías:** [Tipografías a través de la API integrada](./perf-fonts.md)
- **Scripts:** [Scripts de terceros e incrustaciones](./perf-third-party-scripts.md)
- **Navegación:** [Prefetching y transiciones de vista](./perf-navigation.md)

## Estructura del proyecto

- **Rutas:** [Responsabilidad de las rutas, layouts y slots](./arch-route-responsibility.md)
- **Componentes:** [Componentes reutilizables y componentes específicos de página](./arch-component-reuse.md)
- **Imports:** [Alias de rutas de TypeScript](./arch-path-aliases.md)
- **Marcado:** [Disciplina de marcado bajo el compilador de la v7](./arch-markup-discipline.md)

## Estilos

- **Configuración:** [Configuración de TailwindCSS v4 y tokens de tema](./style-tailwind-v4-setup.md)
- **Ámbito:** [Estilos de componente con ámbito](./style-scoped-css.md)

## Compilación y configuración

- **i18n:** [Internacionalización desde el primer día](./build-i18n-day-one.md)
- **Registro:** [Registro estructurado de la compilación](./build-logging.md)
- **Entorno:** [Entorno tipado y política de seguridad de contenido](./build-env-and-csp.md)
- **Despliegue:** [Destino de despliegue y mínimo del toolchain](./build-deployment-target.md)
