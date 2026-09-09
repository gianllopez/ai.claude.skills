---
title: Prefetching y transiciones de vista
impact: MEDIUM
description: Usa la configuración de prefetch integrada y el ClientRouter para la sensación de navegación, con transiciones expresadas en CSS en lugar de un runtime de animación en JavaScript, y movimiento que respeta la preferencia de movimiento reducido.
tags: navigation, prefetch, view-transitions, motion, performance
---

## Prefetching y transiciones de vista

**Impacto (MEDIUM):** El momento más débil de un sitio multipágina es el hueco entre hacer clic en un enlace y el pintado de la página siguiente, y las dos cosas que lo cierran vienen integradas y son ambas una línea de configuración. El prefetching inicia la petición durante el hover o el scroll, así que la navegación se resuelve contra una caché caliente; el `<ClientRouter />` transforma las partes compartidas de la página en lugar de repintarlas, así que la transición se lee como continua. Lo que convierte esto en una regla y no en un consejo es aquello a lo que se recurre en su lugar: un router de cliente, o una librería de animación añadida para producir un fundido que _CSS_ ya hace. Ambos renuncian al modelo de una página por documento — la razón por la que el sitio es rápido — para resolver un problema que el framework ya había resuelto gratis. Las integraciones que antes hacían falta aquí ya no están: `@astrojs/prefetch` se absorbió en el núcleo, y `<ViewTransitions />` se eliminó en la v6 en favor de `<ClientRouter />`.

**Directrices:**

1.  **Activa el prefetching en la configuración, y después ajústalo enlace por enlace:**
    - `prefetch: { prefetchAll: true, defaultStrategy: 'hover' }` cubre un sitio de contenido normal: los enlaces se calientan al pasar el ratón, lo bastante pronto para importar y lo bastante tarde para ser barato
    - `data-astro-prefetch="viewport"` en los enlaces que lo merecen — una llamada a la acción principal, el siguiente artículo — y `"tap"` en enlaces cuyo destino es caro de construir
    - `data-astro-prefetch="false"` en los enlaces que nunca deberían descargarse especulativamente: endpoints destructivos, cualquier cosa tarifada, cualquier cosa tras un muro de pago
    - `@astrojs/prefetch` está obsoleto; un proyecto que lo siga instalando arrastra un paquete que el núcleo reemplazó
2.  **`<ClientRouter />` una sola vez, en el layout base:**
    - Importado desde `astro:transitions` y renderizado en el head, aplica a todas las páginas que usan ese layout
    - `<ViewTransitions />` era su nombre antes de la v6 y ya no existe
    - En la v7 se eliminaron las interioridades de `astro:transitions` — las constantes de eventos, `createAnimationScope()`, los type guards de eventos. Los hooks del ciclo de vida usan los nombres de evento como cadenas (`astro:before-swap`, `astro:after-swap`, `astro:page-load`)
3.  **Nombra los elementos que persisten a través de la navegación:**
    - `transition:name` en el par de elementos que son la misma cosa en ambas páginas — una tarjeta y la cabecera de artículo que abre, la cabecera del sitio, una imagen hero — y el navegador transforma uno en otro
    - El nombre tiene que ser único por página, así que se deriva del `id` de la entrada en lugar de escribirse fijo en un componente renderizado dentro de una lista
    - `transition:persist` para elementos que deben sobrevivir al intercambio con su estado intacto: un elemento multimedia reproduciéndose, un menú abierto
4.  **Expresa el movimiento en CSS:**
    - Las transiciones de vista son un mecanismo de _CSS_; la animación pertenece a una hoja de estilos, no a un runtime de animación en _JavaScript_ cargado para hacer lo que el navegador hace de forma nativa
    - Una transición que necesita una librería suele ser una transición que hace demasiado — las útiles son cortas, y existen para hacer legible un cambio, no para que se noten
    - Cualquier floritura interactiva que sí necesite scripting es una isla, y paga su directiva `client:*` como cualquier otra
5.  **El movimiento es opcional para quien lo ha pedido así:**
    - Envuelve la animación en `@media (prefers-reduced-motion: no-preference)`, o desactiva las transiciones con `<ClientRouter fallback="none" />` bajo esa consulta
    - Esto no es decoración: para algunas personas, el movimiento no solicitado es un desencadenante de síntomas
6.  **El router no cambia lo que el sitio es:**
    - Las páginas siguen siendo documentos, siguen prerenderizadas, siguen siendo direccionables de forma independiente. El `<ClientRouter />` intercambia el documento; no introduce estado de enrutado en el cliente, y nada debería construirse asumiendo que sí

**Incorrecto (un router y una librería de animación reemplazando lo que viene integrado):**

```astro
---
// src/layouts/Base.astro
import { ViewTransitions } from 'astro:transitions'; // eliminado en la v6
import gsap from 'gsap'; // añadido para un fundido cruzado
---

<head>
  <ViewTransitions />
</head>
<body>
  <slot />

  <!-- Mal: un runtime de animación enviado a todas las páginas para hacer lo que
       un keyframe de CSS ya hace, en una transición que el navegador puede
       gobernar por sí mismo -->
  <script>
    document.addEventListener('astro:after-swap', () => {
      gsap.from('main', { opacity: 0, duration: 0.3 });
    });
  </script>
</body>
```

```astro
<!-- Mal: la integración de prefetch que el núcleo reemplazó, y un nombre de
     transición fijo en un componente renderizado una vez por elemento de una lista -->
<a href={`/blog/${post.id}`} transition:name="card">{post.data.title}</a>
```

**Correcto (prefetch y router integrados, movimiento en CSS, movimiento reducido respetado):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'hover',
  },
});
```

```astro
---
// src/layouts/Base.astro
import { ClientRouter } from 'astro:transitions';
---

<html lang="en">
  <head>
    <ClientRouter />
  </head>
  <body>
    <slot />
  </body>
</html>

<style is:global>
  /* La transición es CSS, y solo para quienes no han pedido lo contrario */
  @media (prefers-reduced-motion: no-preference) {
    ::view-transition-old(root) {
      animation: fade-out 120ms ease-out;
    }
    ::view-transition-new(root) {
      animation: fade-in 160ms ease-in;
    }
  }

  @keyframes fade-out {
    to {
      opacity: 0;
    }
  }
  @keyframes fade-in {
    from {
      opacity: 0;
    }
  }
</style>
```

```astro
---
// src/components/PostCard.astro
interface Props {
  post: { id: string; data: { title: string } };
}

const { post } = Astro.props;
---

<!-- Único por entrada, para que la tarjeta se transforme en la cabecera de artículo correcta -->
<a
  href={`/blog/${post.id}`}
  data-astro-prefetch="viewport"
  transition:name={`post-${post.id}`}
>
  {post.data.title}
</a>
```

Referencia: [View transitions](https://docs.astro.build/en/guides/view-transitions/)
