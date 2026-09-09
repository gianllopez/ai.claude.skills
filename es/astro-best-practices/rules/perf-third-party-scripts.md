---
title: Scripts de terceros e incrustaciones
impact: HIGH
description: Mantiene las etiquetas de analítica, los widgets y las incrustaciones fuera del layout global, acotados a las rutas que los necesitan y cargados de forma que no puedan bloquear ni desplazar la página.
tags: performance, scripts, embeds, analytics, layout
---

## Scripts de terceros e incrustaciones

**Impacto (HIGH):** Un script de terceros es código de otro origen, de tamaño desconocido y con un calendario de publicación desconocido, que un proyecto ha aceptado ejecutar en todas las páginas. Puesto en el layout base — que es donde siempre acaba, porque es el único archivo que cubre todo el sitio — un widget de chat añadido para la página de precios se carga también en cada entrada del blog, y un gestor de etiquetas se convierte en un agujero por el que llegan cuantos scripts adicionales sea sin aparecer nunca en un diff. El efecto es que un sitio construido para no enviar casi nada de _JavaScript_ acaba enviando varios cientos de kilobytes del de otra persona, y toda la ventaja del framework se gasta. Las incrustaciones son el mismo problema en forma visible: un iframe de vídeo o una publicación de una red social arrastra su propio runtime y, al no tener espacio reservado, desplaza el artículo a su alrededor cuando carga.

**Directrices:**

1.  **Nada de terceros va en el layout base por defecto:**
    - La pregunta para cada etiqueta es qué rutas la necesitan realmente, y la respuesta rara vez es "todas"
    - Un widget que corresponde a una página corresponde a esa página, o a un componente que esa página renderiza
    - Cuando una etiqueta sí es genuinamente global — un único beacon de analítica — sigue siendo una entrada deliberada, no un contenedor abierto que puede cargar más cosas
2.  **Acota por ruta, y haz visible el alcance:**
    - Una prop del layout (`<Base showChat>`) o un componente por página mantiene la decisión legible en el punto de llamada
    - La alternativa — un script que consulta `location.pathname` antes de hacer nada — ya se ha descargado y ejecutado para cuando decide no ejecutarse
3.  **Cárgalos de forma que no puedan bloquear:**
    - `is:inline` hace que un `<script>` quede fuera del empaquetado, que es lo que suele requerir un snippet de terceros; todo lo demás sigue empaquetado y procesado por _Vite_
    - Las etiquetas no críticas se cargan con `async` o `defer`, y las que solo importan tras una interacción pueden esperar a esa interacción
    - Un script de terceros síncrono en el head es una petición bloqueante del renderizado a un origen que no controlas
4.  **Dale espacio reservado a cada incrustación:**
    - Un iframe con una relación de aspecto fija y dimensiones explícitas no mueve el contenido que tiene debajo cuando carga
    - Cuanto más pesada es la incrustación, más justificada está una fachada — una imagen estática de portada que intercambia la incrustación real al hacer clic, de modo que el runtime llega solo para quienes lo quisieron
5.  **Un gestor de etiquetas es una delegación de esta regla, no una exención:**
    - Es un script que puede cargar arbitrariamente muchos más, ninguno de los cuales pasa por revisión
    - Si es obligatorio, la restricción tiene que aplicarse allí donde se edita el contenedor, y el presupuesto de rendimiento del propio sitio es la vara con la que se mide
6.  **Señales de revisión:**
    - Un `<script src>` que apunta a otro origen, añadido a un layout y no a una página
    - Un iframe sin ancho, alto ni relación de aspecto
    - Cualquier origen de terceros nuevo en la cascada de red que ningún diff introdujo explícitamente

**Incorrecto (todo en el layout base, bloqueante, y una incrustación sin dimensionar):**

```astro
---
// src/layouts/Base.astro
---

<html lang="en">
  <head>
    <!-- Mal: bloquea el renderizado, en todas las páginas, desde un origen que no controlas -->
    <script src="https://cdn.example-analytics.com/tag.js"></script>

    <!-- Mal: un contenedor que puede cargar cuantos scripts adicionales sea, ninguno
         de los cuales aparecerá jamás en un diff -->
    <script is:inline>
      (function (w, d, s, l, i) {
        /* tag manager bootstrap */
      })(window, document, 'script', 'dataLayer', 'GTM-XXXX');
    </script>
  </head>
  <body>
    <slot />

    <!-- Mal: un widget de chat necesario en una página, cargado en todas -->
    <script src="https://widget.example-chat.com/loader.js" is:inline></script>
  </body>
</html>
```

```astro
<!-- Mal: sin dimensiones, así que el artículo se reflowea cuando carga el reproductor -->
<iframe src="https://www.youtube.com/embed/VIDEO_ID"></iframe>
```

**Correcto (acotado a las rutas que lo necesitan, sin bloquear, incrustaciones dimensionadas):**

```astro
---
// src/layouts/Base.astro — la superficie de terceros es una prop, visible en el
// punto de llamada
interface Props {
  title: string;
  description: string;
  showChat?: boolean;
}

const { showChat = false, ...seo } = Astro.props;
---

<html lang="en">
  <head>
    <SeoHead {...seo} />
    <!-- El único beacon global: diferido, y es el único -->
    <script
      is:inline
      defer
      src="https://cdn.example-analytics.com/tag.js"
      data-site="example"></script>
  </head>
  <body>
    <slot />
    {
      showChat && (
        <script
          is:inline
          async
          src="https://widget.example-chat.com/loader.js"
        />
      )
    }
  </body>
</html>
```

```astro
---
// src/pages/pricing.astro — la página que necesita el widget lo pide
import Base from '@layouts/Base.astro';
---

<Base title="Pricing" description="Plans and pricing." showChat>
  <h1>Pricing</h1>
</Base>
```

```astro
---
// src/components/VideoEmbed.astro — espacio reservado, carga diferida
interface Props {
  id: string;
  title: string;
}

const { id, title } = Astro.props;
---

<div class="aspect-video w-full">
  <iframe
    src={`https://www.youtube-nocookie.com/embed/${id}`}
    title={title}
    width="560"
    height="315"
    loading="lazy"
    class="h-full w-full"
    allowfullscreen></iframe>
</div>
```

Referencia: [Scripts and event handling](https://docs.astro.build/en/guides/client-side-scripts/)
