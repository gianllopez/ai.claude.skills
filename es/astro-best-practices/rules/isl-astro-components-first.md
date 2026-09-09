---
title: Componentes .astro antes que componentes de framework
impact: CRITICAL
description: Convierte el componente .astro en la unidad de composición por defecto y hace que recurrir a React, Vue o Svelte sea una decisión que debe nombrar la interactividad que necesita.
tags: components, islands, javascript, composition
---

## Componentes .astro antes que componentes de framework

**Impacto (CRITICAL):** Un componente `.astro` se ejecuta en tiempo de compilación y envía cero bytes de _JavaScript_ — y aun así acepta props, renderiza slots, contiene estilos con ámbito y compone exactamente igual que cualquier otro componente. Por eso la pregunta nunca es "¿puede esto ser un componente `.astro`?"; para cabeceras, tarjetas, pies, navegaciones, secciones y rejillas la respuesta siempre es sí. El defecto es la costumbre: un equipo que llega desde _Next.js_ escribe `Card.tsx` porque eso es lo que un componente significa para ellos, añade `client:load` porque si no no se renderiza como esperan, y envía un runtime de framework más el bundle del componente para renderizar marcado que nunca cambia. Nada falla, y por eso sobrevive a la revisión — la página simplemente carga un runtime que no le sirve de nada, y el coste se acumula con cada componente escrito igual.

**Directrices:**

1.  **`.astro` es el valor por defecto, y ese valor por defecto cubre casi toda la página:**
    - Layouts, cabeceras, barras de navegación, pies, tarjetas, rejillas, secciones hero, tablas, listas, migas de pan, cuerpos de artículo — cualquier cosa cuya salida la deciden sus props
    - Props, slots, slots con nombre y estilos con ámbito funcionan todos; no hay ninguna carencia expresiva que haya que rodear
    - El frontmatter se ejecuta en el servidor en tiempo de compilación, así que la obtención de datos, el acceso al sistema de archivos y los secretos van ahí
2.  **Un componente de framework se gana su lugar con estado en el cliente:**
    - Interactividad real: un formulario con validación en vivo, una lista filtrable, un carrusel, un gráfico que el usuario manipula, un buscador, un widget con estado
    - Un componente existente del sistema de diseño del proyecto que ya existe en _React_ y no vale la pena reescribir
    - Una _API_ del navegador que el componente envuelve — un mapa, un editor, un reproductor
3.  **Interactividad no es lo mismo que framework:**
    - Un desplegable, un toggle de menú, un botón de copiar al portapapeles y un selector de tema son `.astro` más una etiqueta `<script>` o unas pocas líneas de _CSS_ — un runtime de framework para alternar una clase es la respuesta más pesada posible
    - `<script>` dentro de un archivo `.astro` se empaqueta y procesa con _Vite_ como cualquier otro módulo; no es un recurso de último momento, es la herramienta para interacciones pequeñas
4.  **Un componente de framework que no se hidrata sigue siendo un componente `.astro` con pasos de más:**
    - Renderizado sin una directiva `client:*` produce _HTML_ estático y no envía nada — lo cual funciona, pero significa que el framework no aportó nada y que ahora el archivo necesita el toolchain de ese framework para entenderse
    - Si un componente nunca se hidrata en ninguno de los sitios donde se importa, debería ser `.astro`
5.  **Mantén la frontera del framework tan pequeña como la interactividad:**
    - Cuando un control interactivo vive dentro de una sección estática, el componente de framework es el control, no la sección — ver la regla de directivas de hidratación
    - El contenido estático entra en una isla a través de slots, de modo que se renderiza una vez en tiempo de compilación en lugar de ser re-renderizado por el runtime del cliente
6.  **Lo que esta skill no gobierna:**
    - Una vez que existe una isla de _React_, todo lo que ocurre dentro de ella — efectos, estado, valores derivados, la capa de consultas, el tipado — lo gobierna `react-core-best-practices`, que un proyecto que renderiza islas carga junto a esta skill

**Incorrecto (un componente de framework y un runtime para renderizar marcado estático):**

```tsx
// src/components/ServiceCard.tsx — sin estado, sin efectos, sin eventos
type Props = { title: string; description: string; href: string };

export function ServiceCard({ title, description, href }: Props) {
  return (
    <article className="card">
      <h3>{title}</h3>
      <p>{description}</p>
      <a href={href}>Learn more</a>
    </article>
  );
}
```

```astro
---
// src/pages/services.astro
import { ServiceCard } from '@components/ServiceCard';
const services = await getServices();
---

<!-- Mal: envía el runtime de React más el bundle de este componente para que el
     navegador pueda re-renderizar marcado que ya venía correcto en la respuesta HTML -->
{services.map((service) => <ServiceCard client:load {...service} />)}
```

**Correcto (`.astro` para el marcado, un componente de framework solo para la parte con estado):**

```astro
---
// src/components/ServiceCard.astro — cero JavaScript, la misma capacidad
interface Props {
  title: string;
  description: string;
  href: string;
}

const { title, description, href } = Astro.props;
---

<article class="card">
  <h3>{title}</h3>
  <p>{description}</p>
  <a href={href}>Learn more</a>
</article>

<style>
  .card {
    display: grid;
    gap: 0.5rem;
  }
</style>
```

```astro
---
// src/pages/services.astro
import ServiceCard from '@components/ServiceCard.astro';
import ServiceFilter from '@components/ServiceFilter'; // React: estado real en el cliente
const services = await getServices();
---

<!-- El filtro es interactivo, así que es una isla; las tarjetas no -->
<ServiceFilter client:visible categories={categories} />

{services.map((service) => <ServiceCard {...service} />)}
```

Referencia: [Astro components](https://docs.astro.build/en/basics/astro-components/)
