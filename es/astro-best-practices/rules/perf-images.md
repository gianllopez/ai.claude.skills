---
title: Manejo de imágenes y estabilidad del layout
impact: HIGH
description: Exige que las imágenes pasen por los componentes integrados Image y Picture con dimensiones intrínsecas, un tratamiento deliberado del LCP para el hero, y carga diferida en todo lo que esté por debajo del pliegue.
tags: images, assets, performance, cls, lcp
---

## Manejo de imágenes y estabilidad del layout

**Impacto (HIGH):** Un `<img src="/hero.png">` en crudo dentro de un proyecto _Astro_ se salta todo lo que el framework ya hace: sin formato moderno, sin compresión, sin `srcset` generado y — porque el archivo se sirve desde `public/` sin tocar — sin `width` ni `height` intrínsecos en el marcado. Esto último es la parte cara. Sin dimensiones el navegador no reserva espacio, así que cada imagen de la página desplaza el contenido que tiene debajo al decodificarse, y quien lee pierde su sitio en una página que ya se había renderizado. El defecto espejo es tratar todas las imágenes igual: cargar el hero de forma diferida retrasa el elemento más grande de la página más allá del punto en que se mide, así que el arreglo de un problema se convierte en la causa de otro. Las imágenes suelen ser la mayor parte de los bytes de una página, así que aquí es donde un framework de tiempo de compilación se paga a sí mismo o no.

**Directrices:**

1.  **Importa las imágenes locales y renderízalas con `<Image />`:**
    - `import hero from '../assets/hero.png'` le da a _Astro_ las dimensiones y el archivo, así que emite un formato moderno, comprime, y escribe `width` y `height` en el marcado
    - Las imágenes en `public/` se copian literalmente y no las optimiza nada. Ese es el lugar correcto para un favicon o una imagen _OG_ referenciada por _URL_, y el lugar equivocado para las imágenes de contenido
    - El componente exige `alt`, y ese es justamente el punto: una imagen sin texto alternativo tiene que declararlo con `alt=""`
2.  **`<Picture />` cuando el navegador deba elegir:**
    - `formats={['avif', 'webp']}` emite elementos `<source>` y deja que el navegador tome el mejor que soporte
    - Es también la herramienta para la dirección de arte — un recorte distinto en pantallas pequeñas, en lugar de la misma imagen ancha reducida
3.  **El hero no es diferido:**
    - La imagen más grande por encima del pliegue suele ser el elemento que decide el largest-contentful-paint de la página, y debería cargarse con avidez: `loading="eager"` con `fetchpriority="high"`
    - Todo lo que está por debajo del pliegue es `loading="lazy"`, que es el valor por defecto del componente — así que la regla en la práctica es "marca el hero, deja el resto en paz"
    - `decoding="async"` en imágenes no críticas mantiene el trabajo de decodificación fuera del camino hacia el primer pintado
4.  **Describe el layout para que se sirva el archivo correcto:**
    - `widths` y `sizes` juntos le dicen al navegador qué candidato descargar; `sizes` describe el ancho renderizado en cada breakpoint, y equivocarse significa que un móvil se descarga el archivo de escritorio
    - `densities` cubre el caso más simple de una imagen de ancho fijo en pantallas de alta densidad
    - La prop `layout` aplica un comportamiento responsive sin escribir a mano ninguno de los dos
5.  **Las imágenes remotas necesitan autorización para ser optimizadas:**
    - Una imagen de otro origen no se procesa a menos que ese origen esté listado en `image.domains` o lo capture `image.remotePatterns`
    - Incluso sin optimizar, pasarla por `<Image />` con `width` y `height` explícitos sigue comprando estabilidad de layout — que es la mayor parte del beneficio
6.  **Trata el manejo de imágenes como un estándar de compilación en las páginas con muchas imágenes:**
    - Una galería, un índice de casos de estudio o una rejilla de productos multiplica cada una de estas decisiones por el número de elementos, así que el componente y sus props pertenecen a un único componente de tarjeta y no a cada punto de llamada
    - Una página que renderiza imágenes desde contenido debería obtener sus dimensiones del modelo de contenido, no de marcado escrito entrada por entrada

**Incorrecto (etiquetas en crudo desde `public/`, sin dimensiones, hero con carga diferida):**

```astro
---
// src/pages/index.astro
---

<!-- Mal: servido sin tocar desde public/, sin width ni height, así que la página
     se reflowea al decodificar — y el hero es lazy, así que se descarga tarde -->
<img src="/hero.png" alt="Product screenshot" loading="lazy" />

<section class="gallery">
  <!-- Mal: el mismo problema, una vez por elemento -->
  {items.map((item) => <img src={item.image} alt={item.name} />)}
</section>
```

**Correcto (importado, dimensionado, hero priorizado, el resto diferido):**

```astro
---
// src/pages/index.astro
import { Image, Picture } from 'astro:assets';
import hero from '../assets/hero.png';
import GalleryCard from '@components/GalleryCard.astro';

const items = await getItems();
---

<!-- El candidato a LCP: eager, prioridad alta, y dimensionado para el viewport -->
<Image
  src={hero}
  alt="The dashboard showing a completed migration"
  loading="eager"
  fetchpriority="high"
  widths={[480, 960, 1440]}
  sizes="(max-width: 768px) 100vw, 960px"
/>

<!-- Por debajo del pliegue: el navegador elige el formato, el componente difiere la carga -->
<Picture
  src={diagram}
  formats={['avif', 'webp']}
  alt="How the ingest pipeline is structured"
  decoding="async"
/>

<section class="gallery">
  {items.map((item) => <GalleryCard item={item} />)}
</section>
```

```astro
---
// src/components/GalleryCard.astro — las props se deciden una vez, no por llamada
import { Image } from 'astro:assets';

interface Props {
  item: { name: string; image: ImageMetadata };
}

const { item } = Astro.props;
---

<article>
  <Image
    src={item.image}
    alt={item.name}
    widths={[240, 480]}
    sizes="(max-width: 768px) 50vw, 240px"
    decoding="async"
  />
  <h3>{item.name}</h3>
</article>
```

Referencia: [Images](https://docs.astro.build/en/guides/images/)
