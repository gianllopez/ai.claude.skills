# Buenas prácticas de Astro

**Versión 1.0.0**  
_Gian López_  
_Septiembre de 2026_

> **Nota:**  
> Este documento está dirigido principalmente a agentes y LLMs que mantienen,  
> generan o refactorizan bases de código de _Astro_. Las personas  
> también pueden encontrarlo útil, pero la guía está optimizada para la  
> automatización y la consistencia en flujos asistidos por IA.

---

## Resumen

Estándares para construir sitios web de producción con _Astro_ 7, donde la decisión determinante es cuán poco de la página llega al navegador como _JavaScript_. La salida estática es el valor por defecto y el renderizado bajo demanda es la excepción que tiene que justificarse; un componente es un componente `.astro` hasta que la interactividad demuestre lo contrario, y una isla lleva la directiva de hidratación que su posición se gana en lugar de `client:load` en todas partes. El contenido es una colección tipada a través de la Content Layer API, porque un esquema es el único lugar donde un campo obligatorio se convierte en un fallo de compilación en vez de una etiqueta ausente en producción. El SEO se trata como un sistema generado desde ese esquema — una regla de canonical, una convención de barra final, un sitemap que solo lista URLs indexables, JSON-LD derivado del modelo de contenido — nunca compuesto página por página. Los recursos, las tipografías, los scripts de terceros y la navegación siguen las APIs integradas que ya los resuelven, los estilos se resuelven mediante tokens de tema de _TailwindCSS_ v4 declarados en CSS, y la configuración cubre el mínimo de versión, la frontera del entorno y la política de seguridad de contenido que las fuentes omiten. La versión de referencia es _Astro_ 7; cada regla que nombra una clave de configuración o una ruta de importación lleva la versión a la que pertenece. La dirección de diseño visual y la auditoría de accesibilidad quedan fuera de alcance por diseño.

---

## Tabla de contenidos

1. [Renderizado e hidratación](#1-renderizado-e-hidratación) — `CRITICAL`
   - [1.1 Salida estática por defecto](#11-salida-estática-por-defecto)
   - [1.2 Componentes .astro antes que componentes de framework](#12-componentes-astro-antes-que-componentes-de-framework)
   - [1.3 Directivas de hidratación y fronteras de isla](#13-directivas-de-hidratación-y-fronteras-de-isla)
2. [Modelo de contenido](#2-modelo-de-contenido) — `CRITICAL`
   - [2.1 Colecciones de contenido a través de la Content Layer API](#21-colecciones-de-contenido-a-través-de-la-content-layer-api)
   - [2.2 El esquema es el contrato de publicación](#22-el-esquema-es-el-contrato-de-publicación)
   - [2.3 Markdown, MDX y el componente Code](#23-markdown-mdx-y-el-componente-code)
3. [Sistema de SEO](#3-sistema-de-seo) — `CRITICAL`
   - [3.1 URL del sitio, metadatos y canonicals](#31-url-del-sitio-metadatos-y-canonicals)
   - [3.2 Higiene de URLs, redirecciones y migración](#32-higiene-de-urls-redirecciones-y-migración)
   - [3.3 Higiene del sitemap y los feeds](#33-higiene-del-sitemap-y-los-feeds)
   - [3.4 Datos estructurados generados desde el contenido](#34-datos-estructurados-generados-desde-el-contenido)
4. [Recursos y rendimiento](#4-recursos-y-rendimiento) — `HIGH`
   - [4.1 Manejo de imágenes y estabilidad del layout](#41-manejo-de-imágenes-y-estabilidad-del-layout)
   - [4.2 Tipografías a través de la API integrada](#42-tipografías-a-través-de-la-api-integrada)
   - [4.3 Scripts de terceros e incrustaciones](#43-scripts-de-terceros-e-incrustaciones)
   - [4.4 Prefetching y transiciones de vista](#44-prefetching-y-transiciones-de-vista)
5. [Estructura del proyecto](#5-estructura-del-proyecto) — `HIGH`
   - [5.1 Responsabilidad de las rutas, layouts y slots](#51-responsabilidad-de-las-rutas-layouts-y-slots)
   - [5.2 Componentes reutilizables y componentes específicos de página](#52-componentes-reutilizables-y-componentes-específicos-de-página)
   - [5.3 Alias de rutas de TypeScript](#53-alias-de-rutas-de-typescript)
   - [5.4 Disciplina de marcado bajo el compilador de la v7](#54-disciplina-de-marcado-bajo-el-compilador-de-la-v7)
6. [Estilos](#6-estilos) — `HIGH`
   - [6.1 Configuración de TailwindCSS v4 y tokens de tema](#61-configuración-de-tailwindcss-v4-y-tokens-de-tema)
   - [6.2 Estilos de componente con ámbito](#62-estilos-de-componente-con-ámbito)
7. [Compilación y configuración](#7-compilación-y-configuración) — `HIGH`
   - [7.1 Internacionalización desde el primer día](#71-internacionalización-desde-el-primer-día)
   - [7.2 Registro estructurado de la compilación](#72-registro-estructurado-de-la-compilación)
   - [7.3 Entorno tipado y política de seguridad de contenido](#73-entorno-tipado-y-política-de-seguridad-de-contenido)
   - [7.4 Destino de despliegue y mínimo del toolchain](#74-destino-de-despliegue-y-mínimo-del-toolchain)

---

## 1. Renderizado e hidratación

### 1.1 Salida estática por defecto

**Impacto (CRITICAL):** Esta es la decisión que heredan todas las demás reglas de rendimiento. Una página prerenderizada es un archivo en un CDN — no tiene arranque en frío, ni dependencia en tiempo de ejecución, ni coste por solicitud, y no puede fallar en tiempo de solicitud porque no hay nada que ejecutar. Una página bajo demanda renuncia a todo eso, y renuncia por cada solicitud, para siempre. El defecto casi nunca es una decisión deliberada de renderizar en el servidor; es un `output: 'server'` puesto una sola vez para que una ruta pudiera leer una cookie, convirtiendo en silencio todo un sitio de marketing en un runtime. Declarar el modo explícitamente es lo que hace visible el desajuste: cuando la configuración dice que el sitio es estático y una ruta necesita el servidor, la excepción aparece en el diff de esa ruta, donde alguien que revisa puede preguntar qué datos de tiempo de solicitud la justifican.

**Directrices:**

1.  **Declara el modo, aunque sea el valor por defecto:**
    - `output: 'static'` es lo que _Astro_ hace sin configuración alguna, y escribirlo sigue mereciendo la línea — declara la arquitectura, de modo que un `output: 'server'` posterior se lea como un cambio a esa arquitectura y no como configuración inicial
    - El prerenderizado es justamente el motivo para elegir _Astro_. Un proyecto que lo renderiza todo bajo demanda ha pagado un paso de compilación y ha renunciado a la razón de tenerlo
2.  **Adopta el renderizado bajo demanda ruta por ruta:**
    - Con un adaptador instalado, `export const prerender = false` en una sola página o endpoint renderiza esa ruta bajo demanda y deja estática cualquier otra
    - Existe el inverso para proyectos que de verdad son server-first: bajo `output: 'server'`, `export const prerender = true` devuelve una ruta al tiempo de compilación. Recurre a ese modo solo cuando la mayoría de las rutas necesitan el servidor
    - Se requiere un adaptador para el renderizado bajo demanda, y también para las islas de servidor (`server:defer`) — instalar uno no vuelve dinámico el sitio por sí mismo
3.  **El listón para que una ruta abandone el tiempo de compilación:**
    - Necesita datos que solo existen en tiempo de solicitud: el usuario autenticado, una sesión, una cookie, una consulta que la compilación no puede conocer
    - Necesita datos demasiado volátiles como para recompilar por ellos: inventario, precios, disponibilidad en vivo
    - Acepta un cuerpo de solicitud — un endpoint de formulario, un receptor de webhooks
    - Nada de esto es "el contenido cambia a veces". El contenido que cambia según un calendario es una recompilación, no un renderizado; el contenido que cambia desde un _CMS_ es un build hook o una colección en vivo
4.  **Las páginas de marketing, los blogs, la documentación y las landing pages son estáticas, sin excepción:**
    - Son exactamente las páginas cuyo valor depende de ser rápidas e indexables, y exactamente las páginas sin entrada en tiempo de solicitud
    - Un saludo personalizado en una página por lo demás estática es una isla, no una razón para renderizar la página en el servidor
5.  **Lee el modo como una señal de revisión:**
    - Un diff que añade `output: 'server'` debería nombrar las rutas que lo necesitan. Si la respuesta es "una", la respuesta es `prerender = false` en esa una
    - Un diff que añade un adaptador a un proyecto totalmente estático o está preparando una ruta bajo demanda concreta o es innecesario

**Incorrecto (una ruta dinámica convierte todo el sitio en un runtime):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  // Mal: puesto para que /account pudiera leer una sesión. Ahora cada página de
  // marketing, cada entrada del blog y cada landing page se renderiza por solicitud
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

```astro
---
// src/pages/index.astro — nada aquí necesita un servidor, y se lo lleva igual
import Layout from '@layouts/Base.astro';
import { getCollection } from 'astro:content';

const services = await getCollection('services');
---

<Layout title="Home">
  {services.map((service) => <ServiceCard service={service.data} />)}
</Layout>
```

**Correcto (estático en todas partes, bajo demanda donde la solicitud es la entrada):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  // Declarado, no asumido: el sitio se prerenderiza
  output: 'static',
  // Presente solo para que rutas individuales puedan salirse abajo
  adapter: node({ mode: 'standalone' }),
});
```

```astro
---
// src/pages/account/index.astro — la sesión es entrada de tiempo de solicitud,
// así que esta única ruta abandona el tiempo de compilación y lo declara
export const prerender = false;

import Layout from '@layouts/Base.astro';

const user = await getUserFromSession(Astro.request.headers.get('cookie'));
---

<Layout title="Your account">
  <h1>Welcome back, {user.name}</h1>
</Layout>
```

Referencia: [On-demand rendering](https://docs.astro.build/en/guides/on-demand-rendering/)

### 1.2 Componentes .astro antes que componentes de framework

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

### 1.3 Directivas de hidratación y fronteras de isla

**Impacto (CRITICAL):** Una directiva `client:*` es una orden de compra de _JavaScript_, y la directiva decide cuándo paga el navegador. `client:load` significa que el bundle se solicita y se ejecuta durante la carga inicial de la página, compitiendo con todo lo demás, vea o no el usuario alguna vez el componente; `client:visible` significa que ni siquiera se solicita hasta que el componente entra en pantalla, de modo que un gráfico al final de una página larga le cuesta exactamente nada a quien nunca hace scroll. Las dos se ven idénticas en la revisión e idénticas en la página renderizada — la diferencia solo aparece en la cascada de red, y por eso `client:load` se propaga: es la que siempre funciona, así que se convierte en la que siempre se usa. La segunda mitad del defecto es la frontera. Marcar una sección entera como la isla para que funcione un botón hidrata cada párrafo estático que hay dentro, y el framework re-renderiza en el cliente un marcado que ya venía correcto en la respuesta.

**Directrices:**

1.  **Haz que la directiva corresponda a la posición y la prioridad del componente:**
    - `client:load` — por encima del pliegue e interactivo de inmediato: el buscador principal, un carrito en la cabecera, un control que es el tema de la página
    - `client:idle` — necesario pronto pero no primero: widgets secundarios, mejoras no críticas que pueden esperar a que el hilo principal se calme
    - `client:visible` — cualquier cosa por debajo del pliegue. Este es el valor por defecto correcto para la mayoría de las islas, y acepta un `rootMargin` para que la hidratación pueda empezar un poco antes de que el componente entre en el viewport
    - `client:media` — un componente que solo existe en ciertos breakpoints, típicamente un panel lateral solo para móvil o un panel solo para escritorio. Hidratar un menú móvil en escritorio es pagar por un componente que el usuario no puede alcanzar
    - `client:only` — sin renderizado en servidor en absoluto, para componentes que no pueden ejecutarse fuera del navegador. Exige nombrar el framework y cuesta un espacio en blanco hasta la hidratación, así que es un último recurso, no una forma de silenciar un error de desajuste
2.  **`client:load` es una afirmación que tiene que ser cierta:**
    - La afirmación es "el usuario puede interactuar con esto antes de hacer scroll". Si no puede, la directiva está mal
    - Un componente al que solo se llega tras hacer clic en otra cosa no está por encima del pliegue en ningún sentido significativo
    - Al auditar un sitio existente, la victoria más rápida suele ser releer cada `client:load` del código y hacerse esa única pregunta
3.  **Traza la isla alrededor de la interactividad, no alrededor de la sección:**
    - La isla es el control de filtrado, no la sección de resultados; los botones de las pestañas, no los paneles; el formulario, no la página que lo contiene
    - El contenido estático llega a una isla a través de slots, así que se renderiza una vez en tiempo de compilación y se pasa como _HTML_ en lugar de ser re-renderizado por el cliente
4.  **Las islas se hidratan de forma independiente, y esa es una propiedad estructural que conviene aprovechar:**
    - A diferencia de una aplicación de página única, una isla pesada al final de la página no bloquea una isla ligera arriba — cada una se solicita y se hidrata según su propio calendario
    - Así que la estructura correcta no es "menos islas", es "cada isla con su precio correcto". Varias islas pequeñas y bien dirigidas superan a una grande que hidrata todo de golpe
5.  **Aplaza el trabajo de servidor con islas de servidor en lugar de enviarlo al cliente:**
    - `server:defer` renderiza un componente bajo demanda después del esqueleto estático, manteniendo la página prerenderizada mientras un fragmento personalizado o lento llega por separado
    - Esta es la respuesta a "la página es estática salvo por esta franja dinámica" — necesita un adaptador, y no hidrata nada en el cliente
6.  **Una directiva es una señal de revisión cuando falta en el razonamiento del diff:**
    - El hallazgo no es "esto usa `client:load`"; es "esto usa `client:load` y está por debajo del pliegue"
    - Un componente sin ninguna directiva es _HTML_ estático — correcto y gratis cuando el componente no tiene comportamiento, y un error solo cuando se suponía que el componente era interactivo

**Incorrecto (todo hidratado de inmediato, y la isla trazada alrededor de contenido estático):**

```astro
---
// src/pages/pricing.astro
import PricingSection from '@components/PricingSection'; // React
import ComparisonChart from '@components/ComparisonChart'; // React, pesado
import MobileNav from '@components/MobileNav'; // React
---

<!-- Mal: la sección entera es una isla para que funcione un toggle que hay dentro.
     Cada titular, párrafo y precio se re-renderiza en el cliente -->
<PricingSection client:load plans={plans} />

<!-- Mal: por debajo del pliegue, y su bundle se solicita durante la carga inicial -->
<ComparisonChart client:load data={comparison} />

<!-- Mal: hidratado en todos los viewports, incluidos los que nunca lo muestran -->
<MobileNav client:load links={links} />
```

**Correcto (la frontera envuelve la parte interactiva, y cada directiva tiene su precio):**

```astro
---
// src/pages/pricing.astro
import PlanCard from '@components/PlanCard.astro'; // marcado estático, cero JS
import BillingToggle from '@components/BillingToggle'; // React: el único estado aquí
import ComparisonChart from '@components/ComparisonChart'; // React, pesado
import MobileNav from '@components/MobileNav'; // React
---

<section>
  <h2>Pricing</h2>

  <!-- La isla es el toggle, no la sección que lo rodea -->
  <BillingToggle client:load />

  <!-- Las tarjetas estáticas siguen siendo estáticas -->
  {plans.map((plan) => <PlanCard plan={plan} />)}
</section>

<!-- Por debajo del pliegue: su JavaScript no se solicita hasta que el lector llega -->
<ComparisonChart client:visible={{ rootMargin: '200px' }} data={comparison} />

<!-- Solo se hidrata en los viewports que de verdad pueden abrirlo -->
<MobileNav client:media="(max-width: 768px)" links={links} />
```

Referencia: [Template directives reference](https://docs.astro.build/en/reference/directives-reference/)

---

## 2. Modelo de contenido

### 2.1 Colecciones de contenido a través de la Content Layer API

**Impacto (CRITICAL):** El contenido leído a mano es contenido sin contrato. Una página que hace `post.data.title` contra un archivo _Markdown_ recogido con un glob manual obtiene `undefined` justo en la entrada donde la clave del frontmatter estaba mal escrita, renderiza un `<h1>` vacío y se publica — porque nada en la cadena sabía que ese campo era obligatorio. Una colección convierte eso en un fallo de compilación con la ruta del archivo dentro. El segundo coste es que esta _API_ ha cambiado dos veces: la forma anterior a la v6 (`src/content/config.ts`, colecciones sin `loader`) fue **eliminada**, no marcada como obsoleta, así que los tutoriales y el código generado que todavía la enseñan producen un proyecto que no compila. Dejar por escrito la forma actual es lo que evita que una base de código se reconstruya contra documentación que ya no aplica.

**Directrices:**

1.  **Un único archivo de configuración, en la raíz de `src/`:**
    - El archivo es `src/content.config.ts` — no `src/content/config.ts`, que era la ubicación anterior a la v6 y ya no funciona
    - Exporta un único objeto `collections` que asocia cada nombre de colección a una llamada a `defineCollection()`
2.  **Cada colección declara un `loader`:**
    - `glob()` de `astro/loaders` para archivos en disco: `glob({ pattern: '**/*.md', base: './src/data/blog' })`
    - `file()` para un único archivo de datos que contiene muchas entradas
    - Un loader propio o de terceros para un _CMS_ o una _API_ — esta es la costura que hace intercambiable el origen del contenido sin tocar las páginas que lo leen
    - No existe un loader implícito. Las colecciones heredadas y la bandera `legacy.collections` se eliminaron en la v6, así que una colección sin loader no es una colección heredada, es una colección rota
3.  **Importa `z` desde `astro/zod`:**
    - `astro/zod` es la reexportación que sigue la versión que _Astro_ distribuye
    - `import { z } from 'astro:content'` y `astro:schema` son rutas obsoletas que todavía aparecen por todo el material antiguo
    - El _Zod_ incluido es la **v4**, cuyos formatos de cadena de nivel superior reemplazaron a los encadenados: `z.email()`, `z.url()`, `z.uuid()` en lugar de `z.string().email()` y compañía
4.  **Las entradas se identifican por `id`:**
    - Las entradas de la Content Layer exponen `id`, generado a partir del nombre del archivo salvo que el frontmatter lo sobrescriba. La propiedad `slug` pertenecía a las colecciones heredadas ya eliminadas
    - Por eso las rutas dinámicas son `[id].astro` y construyen sus params a partir de `post.id`, y todo lo que compone una URL — un feed, una entrada del sitemap, un enlace interno — lee `id`
5.  **Nunca leas los archivos de contenido directamente:**
    - `import.meta.glob()` es la herramienta correcta para recoger módulos en general, y es el reemplazo del `Astro.glob()` eliminado, pero el contenido no es un módulo cualquiera: recurrir a cualquiera de los dos para cargar _Markdown_ salta el esquema, la generación de tipos y el cacheo
    - Leer `src/content/` con `fs` en el frontmatter de una página tiene el mismo problema y además se rompe en cuanto el contenido se mueve
6.  **Recurre a las colecciones en vivo cuando el contenido no puede esperar a una recompilación:**
    - `defineLiveCollection()` en `src/live.config.ts` obtiene los datos en tiempo de solicitud, de modo que las ediciones del _CMS_ aparecen sin volver a desplegar — estable desde la v6
    - Es la herramienta para contenido genuinamente en vivo, no una forma de evitar configurar un build hook

**Incorrecto (la forma heredada eliminada, y contenido leído a mano):**

```ts
// ⚠️ src/content/config.ts — esta ruta dejó de leerse en la v6
import { defineCollection } from 'astro:content';
import { z } from 'astro:content'; // ruta de importación obsoleta

const blog = defineCollection({
  // Mal: sin loader. Las colecciones heredadas se eliminaron, así que esto no compila
  schema: z.object({
    title: z.string(),
    contact: z.string().email(), // encadenado de Zod 3; la v4 quiere z.email()
    pubDate: z.coerce.date(),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[slug].astro
// Mal: salta el esquema por completo — un título ausente es undefined en tiempo de
// ejecución, y `slug` ya no existe en las entradas de colección
const posts = Object.values(import.meta.glob('../../content/blog/*.md', { eager: true }));

export async function getStaticPaths() {
  return posts.map((post) => ({ params: { slug: post.frontmatter.slug } }));
}
---

<h1>{Astro.props.post.frontmatter.title}</h1>
```

**Correcto (la forma actual de la Content Layer, tipada de extremo a extremo):**

```ts
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — los params salen del id de la entrada
import { getCollection, render } from 'astro:content';
import Layout from '@layouts/Article.astro';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);

  return posts.map((post) => ({
    params: { id: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await render(post);
---

<Layout title={post.data.title} description={post.data.description}>
  <h1>{post.data.title}</h1>
  <Content />
</Layout>
```

Referencia: [Content collections](https://docs.astro.build/en/guides/content-collections/)

### 2.2 El esquema es el contrato de publicación

**Impacto (CRITICAL):** Toda página tiene campos sin los cuales no puede ser correcta — un título, una descripción, una fecha de publicación — y hay exactamente dos lugares donde exigirlos: un esquema que rompe la compilación, o una persona que se acuerda. El segundo funciona hasta que un sitio tiene más de un autor, y entonces se degrada en silencio: una entrada se publica sin meta descripción, una fecha se renderiza como `Invalid Date`, un borrador sale a producción porque nadie lo filtró. Ninguno de estos casos lanza un error. Se descubren semanas después en un informe de rastreo, y para entonces la página ya está indexada tal cual. Un esquema convierte cada uno de ellos en un error de compilación que nombra el archivo y el campo, en el momento en que se escribió el contenido, cuando arreglarlo no cuesta nada. Este es el beneficio concreto de la regla anterior: configurar colecciones vale la pena porque el esquema es donde los requisitos de publicación se vuelven mecánicos.

**Directrices:**

1.  **Declara todos los campos que la plantilla lee:**
    - Si un layout, un feed o un componente lee `post.data.x`, entonces `x` pertenece al esquema — un campo opcional que la plantilla no protege es el mismo defecto que uno no declarado
    - Dale a un campo un `.default()` cuando el sitio tenga un valor de reserva razonable, y déjalo obligatorio cuando no lo tenga. `draft: z.boolean().default(false)` es correcto; un título con valor por defecto no
2.  **La línea base de una página guiada por contenido:**
    - `title` y `description` — los dos sin los cuales no se puede componer el head del documento
    - `pubDate`, y `updatedDate` como opcional. Convierte ambos con `z.coerce.date()` para que una fecha mal formada sea un error de compilación en lugar de un `Invalid Date` en la salida renderizada
    - `draft`, con valor por defecto `false` y filtrado en cada lectura, para que el trabajo sin terminar no pueda llegar a una página, un feed o un sitemap
    - Una sobrescritura de canonical, opcional, para los casos genuinos — una URL migrada, una entrada sindicada. Opcional porque una obligatoria invita a poner un valor incorrecto en cada página
    - `tags` y `author` allí donde el sitio los use
3.  **Restringe los valores, no solo los tipos:**
    - `z.string().max(160)` en una descripción atrapa la que se truncará en una página de resultados, en tiempo de compilación
    - `z.enum([...])` para una categoría o un tipo de página, para que una errata no pueda crear una tercera categoría en silencio
    - `.refine()` para una relación que el sistema de tipos no puede expresar — un `updatedDate` anterior a `pubDate` es corrupción de datos, y rechazarlo es una línea
4.  **Nunca falsees la frescura:**
    - `updatedDate` significa que el contenido cambió. Ponerlo en una compilación, un reformateo o una actualización de dependencias lo convierte en ruido, y los consumidores que confían en él (feeds, sitemaps, buscadores) quedan mal informados
    - Esta es una regla sobre lo que el campo significa, y el esquema solo puede exigir que sea una fecha — así que se enuncia aquí para exigirla en la revisión
5.  **Modela las relaciones con `reference()`, no con cadenas libres:**
    - Una entrada relacionada declarada como `reference('blog')` se valida contra la colección, así que una entrada renombrada o eliminada rompe la compilación en lugar de renderizar un enlace muerto
    - Un `z.string()` corriente que guarda el id de una entrada es una clave foránea sin integridad
6.  **Un CMS no elimina el contrato, lo reubica:**
    - Cuando quienes editan publican a través de un _CMS_, los mismos campos obligatorios tienen que existir como campos del _CMS_, y el esquema del loader sigue validando lo que vuelve — una respuesta de _API_ es entrada no confiable como cualquier otra
    - Vale la pena enunciar la frontera explícitamente: quienes editan son dueños del contenido, no del layout. Un _CMS_ que permite a alguien reestructurar una página es un _CMS_ que romperá la página, y el arreglo es el diseño de los campos, no la revisión
    - Esto se sostiene con independencia del proveedor; la elección entre un _CMS_ y colecciones basadas en archivos es una decisión de flujo de trabajo, no técnica

**Incorrecto (un esquema que no tipa nada de lo que el sitio realmente depende):**

```ts
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  // Mal: todo opcional, nada restringido. Una entrada sin descripción compila
  // sin problemas y se publica con una meta etiqueta vacía
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    pubDate: z.string().optional(),
    related: z.array(z.string()).optional(),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — lee campos que el esquema nunca garantizó
const { post } = Astro.props;
---

<meta name="description" content={post.data.description} />
<time>{new Date(post.data.pubDate).toLocaleDateString()}</time>
```

**Correcto (el contrato está declarado, e incumplirlo rompe la compilación):**

```ts
// src/content.config.ts
import { defineCollection, reference } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z
    .object({
      title: z.string().min(1),
      // El truncado en una página de resultados es un error de compilación, no una sorpresa
      description: z.string().max(160),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      // Solo para excepciones genuinas: migraciones, copias sindicadas
      canonicalUrl: z.url().optional(),
      category: z.enum(['engineering', 'product', 'company']),
      // Validado contra la colección: una entrada renombrada rompe la compilación
      related: z.array(reference('blog')).default([]),
      draft: z.boolean().default(false),
    })
    .refine((data) => !data.updatedDate || data.updatedDate >= data.pubDate, {
      message: 'updatedDate cannot precede pubDate',
      path: ['updatedDate'],
    }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — todos los campos que se leen aquí existen con garantía
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  // Los borradores no pueden llegar a una ruta, un feed ni al sitemap
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({ params: { id: post.id }, props: { post } }));
}

const { post } = Astro.props;
---

<meta name="description" content={post.data.description} />
<time datetime={post.data.pubDate.toISOString()}>
  {post.data.pubDate.toLocaleDateString('en', { dateStyle: 'long' })}
</time>
```

Referencia: [Defining a collection schema](https://docs.astro.build/en/guides/content-collections/)

### 2.3 Markdown, MDX y el componente Code

**Impacto (HIGH):** _MDX_ es _Markdown_ que puede importar y ejecutar componentes, y esa capacidad no es gratis: cada archivo _MDX_ se compila como un módulo, puede meter un componente de framework en la página, y deja de ser contenido que alguien sin perfil técnico pueda editar con seguridad. Convertirlo en el formato de autoría por defecto de un blog significa que cien archivos de prosa cargan con la maquinaria que solo cuatro necesitaban. El defecto espejo es recurrir a bloques `<pre>` en crudo o a un resaltador de terceros cuando el código que se renderiza es dinámico, ignorando el resaltador que _Astro_ ya ejecuta. Y en la v7 el procesador que hay debajo de todo esto cambió: **Sätteri es el valor por defecto**, no ejecuta plugins de _remark_ ni de _rehype_, y `@astrojs/markdown-remark` ya no se instala por ti — así que un proyecto que arrastró su cadena de plugins sin tocar la configuración la ha perdido en silencio.

**Directrices:**

1.  **El _Markdown_ plano es el valor por defecto para la prosa:**
    - Artículos, páginas de documentación, entradas de changelog, textos legales — cualquier cosa que sea texto con encabezados, enlaces, listas e imágenes
    - Sigue siendo editable por cualquiera, produce diffs limpios y no puede importar un componente que cambie el coste de la página
2.  **_MDX_ cuando el contenido realmente incrusta componentes:**
    - Una demo en vivo, un gráfico interactivo dentro de un artículo, un aviso personalizado que el sitio define, un formulario incrustado
    - Instálalo deliberadamente con `npx astro add mdx`, y trata la extensión del archivo como una declaración: `.mdx` significa que esta página ejecuta componentes
    - Un componente usado en todos los artículos no es razón para convertir todos los artículos en _MDX_ — eso es un asunto del layout, y el layout ya es un componente
3.  **Los componentes dentro de _MDX_ obedecen las reglas de hidratación:**
    - Un componente `.astro` importado no cuesta nada; un componente de framework sigue necesitando una directiva `client:*` y sigue pagándose
    - La isla que más a menudo se cuela en un sitio es la que entró por un artículo
4.  **`<Code />` para el código que es dinámico en tiempo de compilación:**
    - Los bloques de código delimitados en _Markdown_ ya los resalta _Shiki_ — déjalos en paz
    - `<Code />` de `astro:components` es ese mismo resaltador en forma de componente, y es la herramienta correcta cuando la fuente es una variable, un archivo leído en tiempo de compilación o un valor de un _CMS_
    - **No** hereda `markdown.shikiConfig`. A un bloque `<Code />` que deba coincidir con el tema de los bloques delimitados que lo rodean hay que pasarle `theme` explícitamente, o la página renderiza dos temas distintos
    - `import.meta.glob()` es la forma de que un archivo de tiempo de compilación se convierta en esa variable; `Astro.glob()` se eliminó en la v6
5.  **Configura el procesador en lugar de heredarlo:**
    - **Sätteri** es el valor por defecto en la v7 y no necesita configuración; decláralo explícitamente solo cuando pases feature flags
    - Ejecuta plugins de _mdast_ y _hast_, que son su propio ecosistema — los plugins de _remark_ y _rehype_ no funcionan bajo él
    - Un proyecto con una cadena _remark_/_rehype_ existente vuelve a optar por ella con `processor: unified()` de `@astrojs/markdown-remark`, que ahora hay que instalar explícitamente
    - Las opciones de nivel superior `markdown.remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm` y `smartypants` están obsoletas en favor de opciones pasadas al procesador. Dejarlas ahí es tener una cadena que dejará de aplicarse

**Incorrecto (MDX por defecto, un bloque de código dinámico sin tema, y una cadena de plugins huérfana):**

```js
// astro.config.mjs
export default defineConfig({
  markdown: {
    // Mal: bajo el procesador por defecto de la v7 esto no se aplica — la cadena
    // está configurada, inerte, y nada lo reporta
    remarkPlugins: [remarkToc],
    gfm: true,
    shikiConfig: { theme: 'github-dark' },
  },
});
```

Después, en `src/data/blog/release-notes.mdx` — prosa escrita como _MDX_ por costumbre, con un `<Code />` que nunca recibe un tema, así que se renderiza con el tema por defecto mientras cada bloque delimitado de la página se renderiza en `github-dark`:

```jsx
import { Code } from 'astro:components';

<Code code={snippet} lang="ts" />;
```

**Correcto (formato elegido por archivo, procesador declarado, tema pasado explícitamente):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import remarkToc from 'remark-toc';

export default defineConfig({
  markdown: {
    // Este proyecto tiene una cadena remark existente, así que vuelve a optar
    // por unified en lugar de perderla en silencio bajo Sätteri (el valor
    // por defecto de la v7)
    processor: unified({ remarkPlugins: [remarkToc] }),
    shikiConfig: { theme: 'github-dark' },
  },
});
```

La misma entrada como `src/data/blog/release-notes.md` — _Markdown_ plano, sin imports, con su bloque delimitado ya resaltado por el procesador configurado:

````markdown
We shipped a few things this month.

```ts
const client = createClient({ retries: 3 });
```
````

```astro
---
// src/pages/docs/examples.astro — código dinámico en tiempo de compilación
import { Code } from 'astro:components';

const modules = import.meta.glob('../../examples/*.ts', {
  eager: true,
  query: '?raw',
  import: 'default',
});
const [path, source] = Object.entries(modules)[0];
---

<!-- tema pasado explícitamente para que coincida con los bloques delimitados del resto -->
<Code code={source} lang="ts" theme="github-dark" />
```

Referencia: [Markdown in Astro](https://docs.astro.build/en/guides/markdown-content/)

---

## 3. Sistema de SEO

### 3.1 URL del sitio, metadatos y canonicals

**Impacto (CRITICAL):** `site` es una línea de configuración de la que dependen en silencio varias cosas sin relación entre sí: `Astro.site`, cada _URL_ absoluta construida a partir de ella, la integración de sitemap (que se niega a ejecutarse sin ella) y las etiquetas canonical. Si se omite, ninguna falla de forma ruidosa — el sitemap simplemente no está y los canonicals son relativos o faltan, que es exactamente el modo de fallo que nadie nota hasta que llega un informe de rastreo. El defecto mayor son los metadatos compuestos a mano en cada página. Empieza como tres etiquetas copiadas entre plantillas y acaba siendo un sitio donde un tercio de las páginas comparte una misma descripción, dos páginas reclaman el mismo canonical, y una ruta duplicada para una campaña compite con su propio original. Los metadatos son contenido generado — derivado del modelo de contenido por un único componente — y en cuanto se escriben a mano página por página empiezan a divergir.

**Directrices:**

1.  **Define `site` en `astro.config.mjs`, siempre:**
    - Es el origen de producción, sin barra final: `site: 'https://example.com'`
    - Sin él, `Astro.site` es `undefined`, las _URL_ absolutas se vuelven relativas en silencio, y `@astrojs/sitemap` no emite nada
2.  **Un único componente de head es dueño de los metadatos de todo el sitio:**
    - Recibe `title`, `description` y las sobrescrituras opcionales como props, y todos los layouts lo renderizan — no hay un segundo sitio donde se escriba un `<title>`
    - Los valores por defecto viven en él: el sufijo con el nombre del sitio, la imagen social de reserva, el valor de `robots` por defecto
    - Las reglas por tipo de página también viven ahí. El patrón de título de una entrada de blog, el de una página de servicio, el de la portada — expresados una vez como función del tipo de página, no reescritos archivo por archivo
3.  **Deriva el canonical, no lo escribas:**
    - `new URL(Astro.url.pathname, Astro.site)` es el canonical de casi cualquier página, y al ser derivado no puede contradecir la ruta en la que vive
    - Acepta una prop de sobrescritura para las excepciones genuinas — una _URL_ migrada, una copia sindicada, una vista filtrada que debería apuntar a su padre sin filtrar — y haz que venga del esquema de contenido, para que la excepción sea un dato y sea revisable
    - Un canonical escrito a mano es, con diferencia, la forma más común de que dos páginas acaben afirmando ser la misma página
4.  **Haz que `noindex` sea una decisión con un motivo:**
    - Páginas de agradecimiento, listados filtrados o facetados, resultados de búsqueda interna, rutas de staging, páginas paginadas más allá de la primera cuando el sitio no las quiere indexadas
    - Va en ese mismo componente como una prop, para que una página con `noindex` se vea como tal en el punto de llamada en lugar de quedar escondida en una meta etiqueta suelta
    - El defecto inverso es real y peor: un `noindex` olvidado de un despliegue de staging en una página que debería posicionar
5.  **Las etiquetas de Open Graph y sociales salen de la misma fuente que las propias de la página:**
    - Que `og:title` repita el título de la página y `og:description` repita la descripción es correcto — lo que no es correcto es un segundo par escrito a mano que diverge del primero
    - `og:url` es el canonical. Si pueden discrepar, tarde o temprano discreparán
6.  **Los títulos y las descripciones son contenido, así que pertenecen al esquema:**
    - Las reglas de contenido ya los exigen; esta regla es la que los consume
    - Un tipo de página sin una entrada de contenido detrás — una landing page escrita como ruta — sigue pasando props explícitas, y sigue haciéndolo por el mismo componente

**Incorrecto (`site` ausente, metadatos escritos página por página, canonical a mano):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // Mal: sin `site`. Astro.site es undefined y el sitemap no emite nada
  integrations: [sitemap()],
});
```

```astro
---
// src/pages/services/migration.astro
---

<html lang="en">
  <head>
    <!-- Mal: tres etiquetas copiadas de otra página, una de ellas sin actualizar.
         El canonical está escrito a mano y apunta a la página de la que se copió -->
    <title>Migration services</title>
    <meta name="description" content="We help teams move their site." />
    <link rel="canonical" href="https://example.com/services/redesign" />
    <meta property="og:title" content="Website migration | Example" />
  </head>
  <body>
    <slot />
  </body>
</html>
```

**Correcto (`site` definido, un único componente de head, canonical derivado):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',
  integrations: [sitemap()],
});
```

```astro
---
// src/components/SeoHead.astro — el único lugar donde se escriben metadatos
interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
  canonicalOverride?: string;
  noindex?: boolean;
  image?: string;
}

const {
  title,
  description,
  pageType = 'service',
  canonicalOverride,
  noindex = false,
  image = '/og-default.png',
} = Astro.props;

const SITE_NAME = 'Example';

// Reglas de título por tipo de página, declaradas una sola vez
const fullTitle = pageType === 'home' ? SITE_NAME : `${title} | ${SITE_NAME}`;

// Derivado, así que no puede contradecir la ruta en la que se renderiza
const canonical = canonicalOverride ?? new URL(Astro.url.pathname, Astro.site);
const socialImage = new URL(image, Astro.site);
---

<title>{fullTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonical} />
{noindex && <meta name="robots" content="noindex, nofollow" />}

<meta property="og:title" content={fullTitle} />
<meta property="og:description" content={description} />
<meta property="og:url" content={canonical} />
<meta property="og:image" content={socialImage} />
<meta name="twitter:card" content="summary_large_image" />
```

```astro
---
// src/layouts/Base.astro — todas las páginas llegan a los metadatos por aquí
import SeoHead from '@components/SeoHead.astro';

interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
  canonicalOverride?: string;
  noindex?: boolean;
}

const props = Astro.props;
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <SeoHead {...props} />
  </head>
  <body>
    <slot />
  </body>
</html>
```

Referencia: [Configuration reference: site](https://docs.astro.build/en/reference/configuration-reference/)

### 3.2 Higiene de URLs, redirecciones y migración

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

### 3.3 Higiene del sitemap y los feeds

**Impacto (HIGH):** Instalar `@astrojs/sitemap` es la mitad fácil y la mitad que todo el mundo hace; lo que emite por defecto es cada ruta que produjo la compilación. Eso incluye la página de agradecimiento, la ruta de resultados de búsqueda interna, la página de staging con `noindex`, el archivo paginado que nadie quiere indexado y — tras una migración — las _URLs_ antiguas que siguen presentes como orígenes de redirección. Un sitemap es una afirmación de que estas son las páginas que vale la pena rastrear, así que enviar uno que contradice los propios canonicals y directivas de robots del sitio es pedirle a un rastreador que elija entre dos respuestas. Los feeds arrastran el mismo problema con un fallo adicional: un feed construido a partir de la propiedad equivocada de la entrada produce enlaces que dan 404 para todas las personas suscritas a la vez, y los lectores de feeds cachean con la suficiente agresividad como para que la versión rota sobreviva al arreglo.

**Directrices:**

1.  **Filtra el sitemap a lo que realmente debe indexarse:**
    - `@astrojs/sitemap` acepta un predicado `filter`, y no es configuración opcional en ningún sitio real
    - Excluye lo que el propio sitio marca como excluido: rutas con `noindex`, páginas de agradecimiento y confirmación, búsqueda interna, listados filtrados o facetados, rutas de vista previa
    - Excluye los orígenes de redirección. Una _URL_ que responde con 301 pertenece al mapa de redirecciones, nunca al sitemap
    - Los borradores ya quedan excluidos aguas arriba, por el filtro de la colección — un borrador que llega a una ruta es un defecto del modelo de contenido, no del sitemap
2.  **El sitemap coincide con el canonical, o está mal:**
    - Mismo origen, misma convención de barra final, misma _URL_ para la misma página
    - `site` tiene que estar definido para que la integración emita algo, cosa que la regla de metadatos ya exige
3.  **`lastmod` significa que el contenido cambió:**
    - Emítelo desde el propio `updatedDate` del contenido, no desde la marca de tiempo de la compilación — un sitemap sellado por el build afirma que todas las páginas cambiaron en cada despliegue, y un consumidor que se lo cree aprende a ignorarlo
    - Cuando no hay una fecha de modificación fiable, omitir `lastmod` es mejor que fabricar una
4.  **Segmenta los sitios grandes en lugar de emitir una lista plana:**
    - La integración pagina automáticamente al pasar su límite de entradas, y `customPages`, `serialize` y las entradas por sección permiten a un sitio expresar prioridad y frecuencia de cambio allí donde de verdad difieren
    - Un archivo de blog y una página de servicio no cambian al mismo ritmo, y decirlo es justamente el propósito de esos campos
5.  **Los feeds se construyen desde la misma fuente filtrada que las páginas:**
    - `@astrojs/rss` recibe la colección, así que hereda el mismo filtro de borradores y el mismo orden
    - Los enlaces se construyen con `context.site` y el `id` de la entrada — las entradas de la Content Layer no tienen `slug`, y un feed construido sobre `post.slug` emite `/blog/undefined/` en cada elemento
    - Define el `pubDate` del elemento desde el campo de fecha del esquema, no desde el mtime del archivo, que cambia al hacer checkout
6.  **Ambos son artefactos generados, así que se revisan en el origen:**
    - Nada de un sitemap o un feed debería mantenerse a mano; una entrada añadida a mano es un hecho que dejará de ser cierto
    - Tras un lanzamiento, descarga el `/sitemap-index.xml` emitido y confirma que el recuento coincide aproximadamente con el número de páginas indexables — una diferencia de un orden de magnitud es la señal más rápida de que falta un filtro

**Incorrecto (todo lo que emitió la compilación, y un feed construido sobre una propiedad eliminada):**

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Mal: sin filtro. Páginas de agradecimiento, búsqueda interna, rutas de vista
  // previa y las URLs antiguas conservadas para redirecciones se envían todas
  // como canónicas
  integrations: [sitemap()],
});
```

```js
// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // Mal: borradores incluidos, y `post.slug` no existe en las entradas de la
  // Content Layer — cada enlace del feed resuelve a /blog/undefined/
  const posts = await getCollection('blog');

  return rss({
    title: 'Example Blog',
    description: 'Notes from the team',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      link: `/blog/${post.slug}/`,
    })),
  });
}
```

**Correcto (filtrado a URLs indexables, feed construido a partir de `id`):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const EXCLUDED = ['/thank-you', '/search', '/preview'];

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',
  integrations: [
    sitemap({
      // Solo las URLs canónicas e indexables llegan al sitemap
      filter: (page) => {
        const { pathname } = new URL(page);
        return !EXCLUDED.some((prefix) => pathname.startsWith(prefix));
      },
    }),
  ],
});
```

```js
// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // El mismo filtro que usan las rutas, para que el feed no pueda contener lo que
  // el sitio no contiene
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );

  return rss({
    title: 'Example Blog',
    description: 'Notes from the team',
    site: context.site,
    items: sorted.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      // `id`, y la convención de barra final del sitio
      link: `/blog/${post.id}`,
    })),
  });
}
```

Referencia: [@astrojs/sitemap](https://docs.astro.build/en/guides/integrations-guide/sitemap/)

### 3.4 Datos estructurados generados desde el contenido

**Impacto (MEDIUM):** Los datos estructurados son una afirmación legible por máquinas sobre lo que contiene una página, y su único valor está en ser ciertos. Copiados a mano en cada plantilla dejan de ser ciertos casi de inmediato: el `datePublished` sigue diciendo la fecha de la página de la que se copió, el `author` nombra a alguien que ya se fue, el `headline` no coincide con el `<h1>` porque se editó uno de los dos. Nada de esto aparece en la página renderizada, así que nada lo detecta — la página se ve correcta y se describe a sí misma de forma incorrecta. Generados desde la misma entrada de contenido que la página renderiza, los dos no pueden discrepar, porque hay una única fuente. La otra mitad de la regla es una frontera: un marcado que afirma cosas que la página no muestra — un bloque de FAQ sin FAQ visible, reseñas que nadie escribió — no es una optimización con un riesgo asociado, es una tergiversación, y es de esas cosas que le cuestan a un sitio sus resultados enriquecidos por completo.

**Directrices:**

1.  **Genera desde la entrada, en un único helper:**
    - Una función que recibe la entrada de contenido y devuelve el objeto, renderizado por el layout mediante un único `<script type="application/ld+json">` — la misma forma que la regla de metadatos, por la misma razón
    - Cada campo que emite se lee del esquema. Un valor escrito como literal dentro del helper es un valor que estará mal en alguna página
    - Serializa con `JSON.stringify` y deja que la plantilla lo inserte, en lugar de componer el _JSON_ como una cadena
2.  **Usa los tipos que corresponden a lo que la página realmente es:**
    - `Article` (o `BlogPosting`) para contenido editorial, `BreadcrumbList` para una página dentro de una jerarquía, `Organization` una sola vez para la identidad del negocio, `Service` para una página de servicio real, `Product` para un producto real
    - Una página suele llevar dos: lo que es, más su miga de pan. Más que eso suele ser una página que se describe a sí misma como varias cosas a la vez
3.  **Describe solo lo que se renderiza:**
    - `FAQPage` exige que las preguntas y respuestas sean visibles en la página, no escondidas tras un desplegable que nunca se abre ni presentes únicamente en el marcado
    - Una valoración exige valoraciones reales y recogidas; una dirección de `Organization` exige una dirección real
    - La prueba es si una persona que abre la página puede ver cada afirmación que hace el marcado. Si no puede, el marcado es el defecto
4.  **_URLs_ absolutas, derivadas como el canonical:**
    - `url`, `image`, `@id` y cada referencia son absolutas, construidas a partir de `Astro.site` — una _URL_ relativa en _JSON-LD_ no se resuelve como se resuelve en _HTML_
    - La `url` de la página es su canonical. Si el helper la calcula por separado, las dos divergirán
5.  **Las fechas salen del esquema y siguen su significado:**
    - `datePublished` desde `pubDate`, `dateModified` desde `updatedDate` — y la regla de contenido contra falsear la frescura aplica aquí en primer lugar, porque este es el sitio donde la afirmación se hace explícita
    - Emítelas como cadenas _ISO_; una fecha formateada según la configuración regional no es válida aquí
6.  **Valida la salida, no la plantilla:**
    - Un helper que produce _JSON_ válido puede seguir produciendo datos estructurados inválidos, así que la comprobación se hace contra una página renderizada
    - Hazlo una vez por tipo de página en lugar de una vez por página — el sentido de generarlos es que un tipo correcto sea correcto en todas partes

**Incorrecto (copiado a mano por página, afirmando contenido que la página no tiene):**

```astro
---
// src/pages/blog/introducing-our-api.astro
---

<!-- Mal: copiado de otra entrada. Las fechas, el autor y el titular son los de
     aquella entrada, y nada de esta página los corregirá nunca -->
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Scaling our ingest pipeline",
    "datePublished": "2025-11-04",
    "author": { "@type": "Person", "name": "A. Former-Employee" },
    "image": "/images/og.png",
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.9",
      "reviewCount": "218"
    }
  }
</script>

<!-- ...y no hay ninguna FAQ en ninguna parte de esta página -->
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Is the API free?",
        "acceptedAnswer": { "@type": "Answer", "text": "Yes." }
      }
    ]
  }
</script>
```

**Correcto (derivado de la entrada, describiendo lo que se renderiza):**

```ts
// src/lib/structured-data.ts
import type { CollectionEntry } from 'astro:content';

export function articleSchema(post: CollectionEntry<'blog'>, site: URL) {
  const url = new URL(`/blog/${post.id}`, site).href;

  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.data.title,
    description: post.data.description,
    url,
    mainEntityOfPage: url,
    datePublished: post.data.pubDate.toISOString(),
    // Presente solo cuando el contenido registra realmente una modificación
    ...(post.data.updatedDate && {
      dateModified: post.data.updatedDate.toISOString(),
    }),
    author: { '@type': 'Person', name: post.data.author },
    publisher: { '@type': 'Organization', name: 'Example' },
  };
}
```

```astro
---
// src/layouts/Article.astro
import type { CollectionEntry } from 'astro:content';
import { articleSchema } from '@lib/structured-data';
import Base from '@layouts/Base.astro';

interface Props {
  post: CollectionEntry<'blog'>;
}

const { post } = Astro.props;
const schema = articleSchema(post, Astro.site!);
---

<Base
  title={post.data.title}
  description={post.data.description}
  pageType="article"
>
  <script
    type="application/ld+json"
    set:html={JSON.stringify(schema)}
    is:inline
  />

  <article>
    <h1>{post.data.title}</h1>
    <slot />
  </article>
</Base>
```

Referencia: [Astro.site and absolute URLs](https://docs.astro.build/en/reference/api-reference/)

---

## 4. Recursos y rendimiento

### 4.1 Manejo de imágenes y estabilidad del layout

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

### 4.2 Tipografías a través de la API integrada

**Impacto (HIGH):** Una fuente web está en el camino crítico del texto, así que toda decisión sobre ella es una decisión sobre cuándo la página se vuelve legible. Cargarla desde un _CDN_ de fuentes de terceros cuesta una resolución _DNS_, una conexión y una ida y vuelta a un origen que el sitio no controla, antes de que se pueda pedir el primer glifo — y entrega la petición de cada visitante a ese tercero, lo que en varias jurisdicciones es una cuestión de privacidad antes que de rendimiento. Montar la alternativa a mano es peor en otra dirección: los bloques `@font-face` escritos a mano omiten habitualmente `font-display`, así que el texto permanece invisible mientras el archivo se descarga, y omiten un fallback con métricas ajustadas, así que la página se reflowea cuando llega la tipografía real. La _API_ integrada convierte todo eso en una entrada de configuración — descarga y autoaloja el archivo, lo subconjunta, genera el fallback, define `font-display` y emite la pista de precarga.

**Directrices:**

1.  **Declara las fuentes en `fonts` dentro de `astro.config.mjs`:**
    - Cada entrada nombra un `provider`, el `name` de la familia y la `cssVariable` que usará el resto del proyecto
    - `fontProviders.fontsource()` y `fontProviders.google()` descargan en tiempo de compilación y autoalojan el resultado — la familia viene del proveedor, los bytes vienen de tu propio origen
    - Un archivo local se declara igual, así que una tipografía con licencia y una pública se configuran de forma idéntica
2.  **Renderiza `<Font />` una sola vez, en el layout base:**
    - Emite las reglas `@font-face` y las pistas de precarga de esa variable
    - `preload` corresponde a la tipografía que se renderiza por encima del pliegue, y solo a esa — precargar todos los pesos los pone a todos en el camino crítico y anula el propósito
3.  **Consume la familia a través de su variable, nunca por nombre:**
    - La `cssVariable` es la referencia única. Una hoja de estilos que además escriba `font-family: 'Inter', sans-serif` a mano tiene una segunda fuente de verdad que la configuración no puede mantener correcta
    - En un proyecto _TailwindCSS_ esta es la costura con el tema: el token de `@theme` se define como esa variable, de modo que `font-sans` resuelve a la tipografía configurada — ver la regla de configuración de _TailwindCSS_
4.  **Carga los pesos y estilos que el diseño usa, y ningún otro:**
    - Cada peso adicional es otro archivo; una fuente variable suele ser un único archivo que cubre todo el rango
    - El conjunto real del diseño es una lista corta, y enviar la familia completa porque era más fácil es un coste que se paga en cada primera visita
5.  **Qué reemplaza esto:**
    - Etiquetas `<link>` a un _CDN_ de fuentes en el head del documento
    - Bloques `@font-face` escritos a mano y los detalles de `font-display`, `unicode-range` y métricas de fallback que los acompañan
    - Archivos de fuente commiteados en `public/` y referenciados por _URL_

**Incorrecto (CDN de terceros, más una face escrita a mano que provoca reflow):**

```astro
---
// src/layouts/Base.astro
---

<head>
  <!-- Mal: resolución DNS, conexión e ida y vuelta a un origen que no controlas,
       antes de que se pida el primer glifo -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
    rel="stylesheet"
  />

  <style is:global>
    /* Mal: sin font-display, así que el texto es invisible mientras esto se
       descarga, y sin fallback con métricas ajustadas, así que la página se
       reflowea cuando llega */
    @font-face {
      font-family: 'Satoshi';
      src: url('/fonts/satoshi.woff2') format('woff2');
    }

    body {
      /* Mal: la familia nombrada a mano, en un segundo lugar */
      font-family: 'Inter', system-ui, sans-serif;
    }
  </style>
</head>
```

**Correcto (declarada una vez, autoalojada, consumida a través de su variable):**

```js
// astro.config.mjs
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  fonts: [
    {
      name: 'Inter',
      cssVariable: '--font-inter',
      provider: fontProviders.fontsource(),
      // Solo lo que el diseño usa
      weights: [400, 600],
      styles: ['normal'],
      subsets: ['latin'],
    },
  ],
});
```

```astro
---
// src/layouts/Base.astro
import { Font } from 'astro:assets';
import '../styles/global.css';
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <!-- precarga solo la tipografía que se renderiza por encima del pliegue -->
    <Font cssVariable="--font-inter" preload />
  </head>
  <body>
    <slot />
  </body>
</html>
```

```css
/* src/styles/global.css — la variable es la única referencia a la familia */
@import 'tailwindcss';

@theme {
  --font-sans: var(--font-inter), system-ui, sans-serif;
}
```

Referencia: [Fonts](https://docs.astro.build/en/guides/fonts/)

### 4.3 Scripts de terceros e incrustaciones

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

### 4.4 Prefetching y transiciones de vista

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

---

## 5. Estructura del proyecto

### 5.1 Responsabilidad de las rutas, layouts y slots

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

### 5.2 Componentes reutilizables y componentes específicos de página

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

### 5.3 Alias de rutas de TypeScript

**Impacto (LOW):** `../../../components/Card.astro` codifica la ubicación del archivo importador dentro del import, así que el import se rompe cuando cualquiera de los dos archivos se mueve — y el fallo es silencioso en el sentido de que un movimiento masivo produce docenas de ellos a la vez, cada uno arreglado contando niveles de directorio. También vuelve los imports ilegibles: quien lee tiene que resolver la ruta mentalmente para saber qué se está importando, y quien revisa no puede saber si dos archivos están importando el mismo módulo. Los alias son unas pocas líneas en `tsconfig.json` que tanto _Astro_ como _Vite_ respetan, y convierten cada import en una afirmación sobre dónde vive un módulo en el proyecto en lugar de dónde está respecto al archivo que lo cita. Esta es la regla de menor impacto de todas — nada se rompe en producción por su causa — pero también es la más barata de adoptar y la más molesta de aplicar a posteriori.

**Directrices:**

1.  **Declara los alias en `tsconfig.json`:**
    - `baseUrl` apuntando a la raíz del proyecto, y una entrada en `paths` por cada directorio de primer nivel desde el que el proyecto importa
    - _Astro_ lee esta configuración a través de _Vite_, así que no hace falta una segunda declaración para el empaquetador
2.  **Un alias por directorio con significado, no un cajón de sastre:**
    - `@components/*`, `@layouts/*`, `@lib/*`, `@styles/*` dicen algo en el punto del import; un `@/*` en solitario reformula la ruta relativa con otro prefijo
    - Mantén un `@/*` general junto a ellos para el módulo ocasional que no encaja en ningún sitio, no como mecanismo principal
    - El conjunto de alias refleja las convenciones de directorios de la regla de responsabilidad de rutas — si un alias nuevo no corresponde a un directorio real, lo que hay que arreglar es la estructura
3.  **Úsalos de forma consistente:**
    - Un archivo que importa a un hermano de forma relativa y a otro por alias hace que ambos sean más difíciles de recorrer. Los imports del mismo directorio son la excepción razonable: `./Card.astro` junto al archivo que lo usa es más claro que una ruta absoluta
    - Los imports de colecciones de contenido (`astro:content`) y los módulos integrados no llevan alias; ya son nombres absolutos
4.  **Aplícalos en todos los sitios donde funcionen:**
    - Imports de componentes y layouts en el frontmatter `.astro`, módulos en archivos `.ts`, e imports dentro de componentes de framework
    - `@styles/global.css` en un layout es la misma idea: la hoja de estilos tiene una ubicación en el proyecto, no relativa a quien la importe

**Incorrecto (cadenas relativas que codifican la ubicación del importador):**

```astro
---
// src/pages/blog/tags/[tag].astro
import Layout from '../../../layouts/Base.astro';
import Card from '../../../components/ContentCard.astro';
import { formatDate } from '../../../lib/dates';
import '../../../styles/global.css';
---
```

**Correcto (alias declarados una vez, imports legibles desde cualquier sitio):**

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@layouts/*": ["src/layouts/*"],
      "@lib/*": ["src/lib/*"],
      "@styles/*": ["src/styles/*"]
    }
  }
}
```

```astro
---
// src/pages/blog/tags/[tag].astro — los mismos imports, desde cualquier sitio
import Layout from '@layouts/Base.astro';
import Card from '@components/ContentCard.astro';
import { formatDate } from '@lib/dates';
import '@styles/global.css';
---
```

Referencia: [TypeScript in Astro](https://docs.astro.build/en/guides/typescript/)

### 5.4 Disciplina de marcado bajo el compilador de la v7

**Impacto (HIGH):** Durante casi toda la historia de _Astro_ el compilador fue indulgente: un `<div>` sin cerrar se aceptaba, el anidamiento inválido se reestructuraba en silencio hacia algo válido, y la página se renderizaba lo bastante parecida a lo que quien la escribió pretendía como para que nadie investigara. En la v7 el compilador de _Rust_ es el valor por defecto y la única opción, y es estricto — **las etiquetas sin cerrar son errores** y el _HTML_ semánticamente inválido **ya no se autocorrige**. Así que un marcado que una base de código ha arrastrado durante años, renderizándose bien, puede romper la compilación al actualizar sin ningún cambio en el archivo que lo contiene. El valor por defecto de los espacios en blanco cambió a la vez: `compressHTML` ahora es `'jsx'`, que elimina espacios usando reglas de _JSX_, así que el espacio entre dos elementos en línea que antes sobrevivía puede desaparecer y pegar dos palabras. Ambos son baratos de cumplir deliberadamente y confusos de diagnosticar a posteriori.

**Directrices:**

1.  **Cierra todas las etiquetas:**
    - Incluidas aquellas que el _HTML_ históricamente permitía dejar abiertas — `<li>`, `<p>`, `<td>`, `<tr>`, `<option>` — porque el compilador ya no infiere dónde terminan
    - Los elementos vacíos se autocierran o se escriben como etiquetas simples de forma consistente: `<br />`, `<img ... />`, `<meta ... />`
    - Las etiquetas de componente siguen la misma regla, y un componente sin cerrar es la versión de esto que más cuesta detectar en una plantilla larga
2.  **Respeta las reglas de anidamiento en lugar de confiar en la reparación:**
    - Un `<div>` dentro de un `<p>`, un `<p>` dentro de un `<p>`, contenido de bloque dentro de elementos en línea, un `<td>` fuera de un `<tr>` — antes se reestructuraban, ahora se dejan tal cual o se rechazan
    - Los elementos interactivos no se anidan: un `<button>` dentro de un `<a>`, un `<a>` dentro de un `<a>`
    - La estructura de tabla es explícita — `<thead>`, `<tbody>`, `<tr>`, `<td>` — en lugar de asumirse
3.  **Sé explícito con los espacios en blanco significativos:**
    - Bajo `compressHTML: 'jsx'`, el espacio entre `</a>` y el siguiente elemento en línea situado en otra línea se elimina, así que `<a>Read</a> <span>more</span>` repartido en varias líneas puede renderizarse como "Readmore"
    - Cuando un espacio es significativo, escríbelo: `{' '}` entre los elementos, o mantenlos en una misma línea
    - El fallo es visual y fácil de pasar por alto en la revisión, así que aparece primero en páginas con enlaces en línea dentro de párrafos
4.  **Los nombres de archivo reservados forman parte de la superficie de enrutado:**
    - `src/fetch.ts` (y `src/fetch.js`) está reservado en la v7 para enrutado avanzado; un proyecto que use esa ruta para un helper propio debe renombrarla o definir `fetchFile`
    - Es el tipo de colisión que produce un error confuso en lugar de uno evidente, así que conviene saberlo antes de la actualización
5.  **Deja que la comprobación sea la compilación:**
    - Esta regla no necesita un linter aparte — el compilador ahora exige la mayor parte de ella, que es justamente el cambio
    - La consecuencia práctica es el orden de la actualización: ejecuta la compilación pronto contra plantillas reales en lugar de descubrir la estrictez en el momento del despliegue

**Incorrecto (marcado que el compilador antiguo reparaba, y un espacio que el nuevo valor por defecto elimina):**

```astro
---
// src/components/ArticleList.astro
---

<ul>
  <!-- Mal: <li> sin cerrar — antes se infería, ahora es un error de compilación -->
  <li><a href="/blog/one">One</a>
  <li><a href="/blog/two">Two</a>
</ul>

<!-- Mal: un div no puede vivir dentro de un p. Antes se reestructuraba, ahora
     se deja inválido -->
<p>
  Introduction text.
  <div class="callout">A note about the above.</div>
</p>

<!-- Mal: elementos interactivos anidados -->
<a href="/pricing"><button>See pricing</button></a>

<p>
  Read the
  <a href="/guide">migration guide</a>
  <em>before</em> starting.
</p>
<!-- Bajo compressHTML: 'jsx' el salto de línea entre los elementos en línea no es
     un espacio, así que esto se renderiza como "…migration guidebefore starting." -->
```

**Correcto (bien formado, correctamente anidado, con el espacio declarado):**

```astro
---
// src/components/ArticleList.astro
---

<ul>
  <li><a href="/blog/one">One</a></li>
  <li><a href="/blog/two">Two</a></li>
</ul>

<p>Introduction text.</p>
<aside class="callout">A note about the above.</aside>

<a href="/pricing" class="button">See pricing</a>

<p>
  Read the <a href="/guide">migration guide</a>{' '}
  <em>before</em> starting.
</p>
```

Referencia: [Upgrade to Astro v7](https://docs.astro.build/en/guides/upgrade-to/v7/)

---

## 6. Estilos

### 6.1 Configuración de TailwindCSS v4 y tokens de tema

**Impacto (HIGH):** En la v4 hay dos formas de instalar _TailwindCSS_ en un proyecto _Astro_ y solo una de ellas es la vigente: `@astrojs/tailwind` es la integración obsoleta de la era v3, y `@tailwindcss/vite` ejecuta el motor dentro de la propia cadena de _Vite_. Un proyecto en el camino antiguo obtiene una pasada de _PostCSS_ aparte, recompilaciones más lentas, y configuración en un archivo que la v4 ya no trata como fuente de verdad. Esa es la mitad de la configuración. La mitad de los tokens es aquello para lo que la configuración existe: en la v4 el tema **es** la hoja de estilos, así que un token declarado genera sus utilidades y expone una variable _CSS_ a la vez, y cada valor arbitrario escrito en un punto de llamada es una decisión de diseño tomada fuera de ese sistema. La costura específica de _Astro_ es la tipografía: la Fonts _API_ produce una variable, y el token del tema tiene que definirse como esa variable, o el proyecto tendrá dos nombres para una misma familia y ninguna garantía de que coincidan.

**Directrices:**

1.  **Instala a través de _Vite_:**
    - `tailwindcss` y `@tailwindcss/vite`, registrados como `vite: { plugins: [tailwindcss()] }` en `astro.config.mjs`
    - `@astrojs/tailwind` está obsoleto. Un proyecto que todavía lo liste en `integrations` está en el camino de la v3 y debería migrar antes de que aplique nada más de aquí
    - No hay `tailwind.config.js` por defecto; una configuración en _JS_ vuelve solo a través de `@config`, y solo cuando un plugin heredado lo requiere
2.  **Una única hoja de estilos global, importada una sola vez:**
    - `@import 'tailwindcss'` al principio de `src/styles/global.css`, y ese archivo importado en el layout base — no en cada página, ni en cada componente
    - El layout base es el punto de entrada único, lo que encaja con la regla de responsabilidad de rutas: el layout es dueño de lo que todas las páginas comparten
3.  **Declara las decisiones de diseño en `@theme`:**
    - Colores, radios, tipografías, breakpoints, sombras y escalones tipográficos viven en el bloque `@theme`, y cada token genera sus utilidades automáticamente — `--color-brand` produce `bg-brand`, `text-brand`, `border-brand`
    - La escala de espaciado es la excepción y no se vuelve a declarar: `--spacing` es de _Tailwind_, y redefinirla cambia todos los márgenes, huecos y tamaños de golpe
    - Dimensiona la capa de tokens al proyecto. Un `@theme` sencillo es un sistema completo para la mayoría de los sitios; la capa `:root` / `.dark` respaldada por variables solo se gana su indirección allí donde algo la lee — un cambio de tema, o un generador de componentes
4.  **Conecta el token de tipografía con la variable de la Fonts _API_:**
    - La `cssVariable` declarada en la configuración `fonts` es la única referencia a la familia, y `--font-sans: var(--font-inter), system-ui, sans-serif` en `@theme` es lo que hace que `font-sans` resuelva a ella
    - Nombrar la familia otra vez en _CSS_ crea una segunda fuente de verdad que la configuración de fuentes no puede mantener correcta
5.  **Los valores arbitrarios son una señal de revisión:**
    - `bg-[#1d4ed8]`, `p-[13px]`, `text-[15px]` significan o bien que el token existe y no se usó, o bien que el token falta y debería añadirse
    - La geometría genuinamente puntual — `grid-cols-[auto_1fr]`, una _URL_ de máscara, un desplazamiento de terceros — es legítima. Un color casi nunca lo es, y un valor de espaciado nunca
6.  **Deja el orden de las clases en manos del formateador:**
    - `prettier-plugin-tailwindcss` ordena los atributos de clase, incluso en archivos `.astro`, así que el orden nunca es un comentario de revisión
    - Las utilidades en conflicto dentro de una misma cadena siguen resolviéndose por orden de la hoja de estilos y no por intención, cosa que ordenar no arregla — eso es un defecto que hay que eliminar, no reordenar
7.  **Dónde se detiene esta skill:**
    - La composición de clases dentro de una isla de _React_, y el helper consciente de fusiones que la hace segura, pertenecen a las skills de _React_ que un proyecto carga junto a esta. Lo que se enuncia aquí es la configuración del proyecto y su capa de tokens

**Incorrecto (integración obsoleta, una configuración JS que la v4 no lee, tokens inventados en el punto de llamada):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind'; // integración obsoleta de la v3

export default defineConfig({
  integrations: [tailwind()],
});
```

```js
// tailwind.config.js — no es la fuente de verdad en la v4
module.exports = {
  theme: {
    extend: {
      colors: { brand: '#1d4ed8' },
      fontFamily: { sans: ['Inter', 'sans-serif'] },
    },
  },
};
```

```astro
---
// src/components/Badge.astro
---

<!-- Mal: el color de marca y el espaciado inventados aquí, y la familia
     tipográfica nombrada por segunda vez, desconectada de la variable
     de la Fonts API -->
<span
  class="rounded-[7px] bg-[#1d4ed8] px-[13px] py-[5px] text-[13px] text-white"
  style="font-family: 'Inter', sans-serif"
>
  <slot />
</span>
```

**Correcto (plugin de Vite, tokens en CSS, tipografía conectada a la variable generada):**

```js
// astro.config.mjs
import { defineConfig, fontProviders } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://example.com',
  vite: { plugins: [tailwindcss()] },
  fonts: [
    {
      name: 'Inter',
      cssVariable: '--font-inter',
      provider: fontProviders.fontsource(),
    },
  ],
});
```

```css
/* src/styles/global.css — el tema es la hoja de estilos */
@import 'tailwindcss';

@theme {
  /* La costura: el token se define como la variable que genera la Fonts API */
  --font-sans: var(--font-inter), system-ui, sans-serif;

  --color-brand: oklch(0.53 0.19 262);
  --color-brand-strong: oklch(0.44 0.19 262);
  --radius-badge: 0.4375rem;
  --text-badge: 0.8125rem;
}
```

```astro
---
// src/layouts/Base.astro — importado una vez, para todo el sitio
import { Font } from 'astro:assets';
import '@styles/global.css';
---

<html lang="en">
  <head>
    <Font cssVariable="--font-inter" preload />
  </head>
  <body class="font-sans">
    <slot />
  </body>
</html>
```

```astro
---
// src/components/Badge.astro — cada valor resuelve a través de un token
---

<span
  class="text-badge rounded-badge bg-brand px-3 py-1 text-white"
>
  <slot />
</span>
```

Referencia: [Install Tailwind CSS with Astro](https://tailwindcss.com/docs/installation/framework-guides/astro)

### 6.2 Estilos de componente con ámbito

**Impacto (MEDIUM):** Un bloque `<style>` en un archivo `.astro` queda acotado a ese componente automáticamente, y solo se emiten las reglas que el componente realmente renderiza — así que los estilos de componente no pueden filtrarse, no pueden ser sobrescritos por un archivo sin relación, y no pueden acumularse en una hoja de estilos global de la que nadie se atreve a borrar nada. `is:global` renuncia a las tres cosas de golpe. Es la herramienta correcta para el puñado de cosas que sí son globales — resets, reglas sobre `body`, dar estilo a marcado del que el componente no es dueño, como la salida de _Markdown_ renderizada mediante `<Content />` — y también es la forma más rápida de convertir un sistema con ámbito en el sistema global que reemplazó, porque hace que un selector rebelde funcione al instante. El defecto relacionado es el atributo `style` en línea usado para pasar un valor: se salta la hoja de estilos por completo, así que el valor no puede ser un token, no puede responder a una media query, y no puede sobrescribirse con nada que no sea `!important`.

**Directrices:**

1.  **Primero las utilidades, y estilos con ámbito para lo que las utilidades no pueden expresar:**
    - En un proyecto _TailwindCSS_ la mayor parte del estilo de componente son atributos de clase, y un bloque con ámbito no es una forma de evitarlos
    - Se gana su lugar para keyframes, selectores complejos, reglas `::view-transition`, comportamiento específico de contenedor, y cualquier cosa genuinamente local que como cadena de utilidades sería ruido
2.  **`is:global` nombra su motivo:**
    - Legítimo: resets y reglas base en la hoja de estilos del layout, dar estilo a la salida de `<Content />` que el componente no escribió, marcado de terceros que el componente envuelve
    - No legítimo: hacer que un selector coincida porque el ámbito estorbaba. Si un estilo tiene que alcanzar a un componente hijo, el hijo debería ser su dueño, o el valor debería viajar como prop
    - `:global()` alrededor de un único selector es la herramienta más estrecha cuando solo parte de una regla debe escapar
3.  **Pasa los valores dinámicos con `define:vars`, no con estilos en línea:**
    - `define:vars={{ accent }}` expone un valor del frontmatter al bloque con ámbito como variable _CSS_, de modo que el valor se queda en la hoja de estilos, donde las variantes y las media queries todavía pueden alcanzarlo
    - Un atributo `style` en línea se reserva para valores genuinamente calculados en tiempo de ejecución en el navegador
4.  **Las hojas de estilo globales se mantienen pequeñas y en un solo sitio:**
    - `src/styles/global.css` contiene el import de _Tailwind_, el tema y el puñado de reglas base — no es donde van los estilos de componente
    - Un estilo de componente que se ha promocionado a global porque dos componentes lo necesitaban suele ser un tercer componente esperando a ser extraído
5.  **Da estilo a lo que el componente posee:**
    - Un componente que se mete en las interioridades de un hijo con un selector descendiente crea un acoplamiento que sobrevive a cada refactor del hijo
    - Cuando un padre debe influir en la apariencia de un hijo, el hijo lo expone — una prop, una prop `class` fusionada en su raíz, un atributo de datos desde el que da estilo

**Incorrecto (escapes globales y un valor en línea):**

```astro
---
// src/components/Callout.astro
const { accent } = Astro.props;
---

<div class="callout">
  <!-- Mal: el valor se salta la hoja de estilos, así que ninguna variante ni
       media query puede alcanzarlo -->
  <span class="callout__bar" style={`background: ${accent}`}></span>
  <slot />
</div>

<style is:global>
  /* Mal: global porque un selector no coincidía. Todos los .callout del sitio
     están ahora estilizados por este componente, incluidos los que nunca renderizó */
  .callout {
    border-left: 4px solid;
    padding: 1rem;
  }

  /* Mal: metiéndose en las interioridades de un componente hijo */
  .callout .card__title {
    font-weight: 700;
  }
</style>
```

**Correcto (con ámbito por defecto, variables para los valores dinámicos, global solo donde debe serlo):**

```astro
---
// src/components/Callout.astro
interface Props {
  accent?: string;
}

const { accent = 'var(--color-brand)' } = Astro.props;
---

<div class="callout">
  <span class="callout__bar"></span>
  <slot />
</div>

<!-- Con ámbito: estas reglas no pueden filtrarse, y solo se emite lo que se renderiza -->
<style define:vars={{ accent }}>
  .callout {
    border-left: 4px solid var(--accent);
    padding: 1rem;
  }

  .callout__bar {
    background: var(--accent);
  }
</style>
```

```astro
---
// src/layouts/Article.astro — global, con un motivo: esto da estilo a la salida
// de Markdown que el layout renderiza pero no escribió
import { render } from 'astro:content';

const { Content } = await render(Astro.props.post);
---

<article class="prose">
  <Content />
</article>

<style is:global>
  .prose h2 {
    margin-block-start: 2rem;
  }

  .prose :where(a) {
    text-decoration: underline;
  }
</style>
```

Referencia: [Styling and CSS](https://docs.astro.build/en/guides/styling/)

---

## 7. Compilación y configuración

### 7.1 Internacionalización desde el primer día

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

### 7.2 Registro estructurado de la compilación

**Impacto (LOW):** Un `console.log` en el frontmatter de un `.astro` se ejecuta en tiempo de compilación e imprime en mitad de la salida de la compilación sin nivel, sin origen y sin marca de tiempo, indistinguible de las propias líneas del framework — así que o se pierde en el ruido o se queda ahí como ruido para todos los demás. Peor aún, una advertencia impresa así no es una advertencia: va a stdout como todo lo demás, así que un trabajo de _CI_ que filtra stderr nunca la ve, y una condición que merecía reportarse — una colección que volvió vacía, una página construida sin elementos — pasa en silencio. `Astro.logger` aporta los niveles, envía los errores a stderr y etiqueta el origen; la opción `logger` estable de nivel superior decide el formato, de modo que el mismo código produce salida legible en local y salida analizable por máquinas en _CI_.

**Directrices:**

1.  **Usa `Astro.logger` en páginas, componentes y endpoints:**
    - `info` para algo que merece decirse una vez por compilación, `warn` para una condición que habría que mirar, `error` para una que debería hacer caer una revisión
    - Los errores van a stderr y todo lo demás a stdout, que es lo que hace que el filtrado por nivel funcione aguas abajo
    - Las integraciones reciben su propio logger a través de los parámetros de los hooks en lugar de recurrir al global
2.  **Registra condiciones, no progreso:**
    - Las líneas valiosas son las que reportan algo inesperado: una colección con cero entradas, una página renderizada con un campo opcional ausente, un valor de reserva que hubo que usar
    - Una línea impresa incondicionalmente en cada compilación es una línea que todo el mundo aprende a saltarse
3.  **Configura el manejador en el nivel superior:**
    - `logger` es un campo de configuración estable de nivel superior desde la v7 — no `experimental.logger`, que es lo que muestra el material anterior a la v7
    - `logHandlers.json({ level: 'info' })` de `astro/config` produce salida estructurada para _CI_ y agregación de logs; un manejador propio se declara con `{ entrypoint, config }`, y el entrypoint debe ser un archivo _JavaScript_
    - La bandera `--json` de la _CLI_ cambia el formato para una única ejecución sin tocar la configuración
4.  **No registres lo que no pertenece a un log de compilación:**
    - Secretos, datos de solicitudes, y objetos completos que se volcarán en cada página de una colección
    - Un log de compilación lo lee quien está diagnosticando un fallo; el volumen es lo que lo vuelve inútil
5.  **El registro en el cliente es otro problema:**
    - El frontmatter se ejecuta en tiempo de compilación, así que `Astro.logger` nunca llega al navegador. Una llamada a `console` dentro de un `<script>` o de una isla es código de cliente, y pertenece a las reglas que gobiernan ese código

**Incorrecto (líneas de progreso sin etiquetar, y una advertencia que no lo es):**

```astro
---
// src/pages/blog/index.astro
import { getCollection } from 'astro:content';

const posts = await getCollection('blog', ({ data }) => !data.draft);

// Mal: sin nivel, sin origen, impreso en cada compilación, perdido en la propia
// salida del framework
console.log('Building blog index');
console.log(posts);

// Mal: esto es una advertencia impresa en stdout, así que el filtrado de CI nunca la ve
if (posts.length === 0) {
  console.log('no posts!');
}
---
```

**Correcto (niveles con significado, manejador configurado según el entorno):**

```js
// astro.config.mjs
import { defineConfig, logHandlers } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  // Campo estable de nivel superior en la v7. Salida estructurada para CI; la
  // bandera --json de la CLI cambia una única ejecución sin editar esto
  logger: logHandlers.json({ level: 'info' }),
});
```

```astro
---
// src/pages/blog/index.astro
import { getCollection } from 'astro:content';

const posts = await getCollection('blog', ({ data }) => !data.draft);

// Reporta una condición, en un nivel que se enruta correctamente
if (posts.length === 0) {
  Astro.logger.warn('Blog index built with no published posts');
}
---

<Layout title="Blog" description="Notes from the team">
  {posts.map((post) => <PostCard post={post} />)}
</Layout>
```

Referencia: [Configuration reference: logger](https://docs.astro.build/en/reference/configuration-reference/)

### 7.3 Entorno tipado y política de seguridad de contenido

**Impacto (HIGH):** `import.meta.env` no está tipado ni validado: una variable ausente es `undefined` en el punto de uso en lugar de un error al arrancar, una errata produce lo mismo, y la regla que mantiene los secretos fuera del navegador es una convención de nombres — una variable que debería haber sido solo de servidor llega al bundle del cliente por leerse en el archivo equivocado, y nada lo reporta. `astro:env` reemplaza la convención por un esquema: cada variable declara su contexto y su acceso, los secretos quedan excluidos del bundle por construcción, y una variable que falta rompe la compilación. La segunda mitad de esta regla es lo que un sitio estático publica sin darse cuenta. La _CSP_ es estable desde la v6 como `security.csp` y funciona en todos los modos de renderizado, calculando hashes para los scripts y estilos propios del sitio — así que la razón por la que falta en la mayoría de los proyectos _Astro_ no es que sea difícil, es que nada la pide.

**Directrices:**

1.  **Declara cada variable en `env.schema`:**
    - `envField.string()`, `.number()`, `.boolean()`, `.enum()` con un `context` y un `access`
    - Las variables con `context: 'client'` están disponibles en ambos bundles y son, por tanto, públicas, siempre
    - `context: 'server'` con `access: 'public'` se queda en el bundle del servidor; con `access: 'secret'` no se empaqueta en absoluto y se lee en tiempo de ejecución
    - No existe una variable de cliente secreta, porque no hay forma segura de enviar una — un valor que el navegador necesita es un valor público, y tratarlo de otro modo es el error que este esquema previene
2.  **Importa desde el módulo específico del contexto:**
    - `import { API_URL } from 'astro:env/client'` e `import { API_SECRET } from 'astro:env/server'`
    - La ruta de importación es la comprobación: un valor solo de servidor arrastrado a un componente que se hidrata es un error de compilación en lugar de una filtración
    - `import.meta.env` sigue funcionando y sigue sin tener nada de esto — es el recurso para valores fuera del esquema, que deberían ser casi ninguno
3.  **Marca como opcionales los valores opcionales, con un valor por defecto:**
    - Una variable declarada obligatoria es una que un despliegue roto no puede saltarse, que es justamente el punto
    - `optional: true` más `default:` para las que sí tienen un valor de reserva razonable
4.  **Activa `security.csp`:**
    - `security: { csp: true }` es la línea base y funciona igual para páginas prerenderizadas y bajo demanda
    - La forma de objeto acepta `algorithm`, `directives`, y `scriptDirective` / `styleDirective` con sus propios `hashes` y `resources` — que es como un sitio declara los orígenes de terceros que realmente carga
    - Cada origen permitido debería corresponder a un script o una incrustación que la regla de terceros ya justificó. Una política que lista orígenes que nadie sabe explicar es una política que ha dejado de significar algo
5.  **Una política se verifica en un navegador, no en la configuración:**
    - El modo de fallo es una directiva demasiado estrecha, que rompe un widget en silencio en producción y solo se ve en la consola
    - Revisa primero las páginas que llevan incrustaciones — son donde la política y el sitio discrepan

**Incorrecto (acceso sin tipar, un secreto leído donde puede empaquetarse, sin política):**

```astro
---
// src/components/ContactForm.astro
// Mal: sin tipar, sin validar. Una variable ausente o mal escrita es `undefined`
const endpoint = import.meta.env.PUBLIC_API_URL;

// Mal: un secreto leído en un componente que se pasa a una isla hidratada —
// nada en la cadena impide que llegue al bundle del navegador
const apiKey = import.meta.env.CRM_API_KEY;
---

<ContactWidget client:visible endpoint={endpoint} apiKey={apiKey} />
```

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Mal: sin esquema de entorno, y sin ninguna política de seguridad de contenido
});
```

**Correcto (declarado en el esquema, separado por contexto, política activada):**

```js
// astro.config.mjs
import { defineConfig, envField } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',

  env: {
    schema: {
      // Pública: segura en ambos bundles, y el navegador realmente la necesita
      PUBLIC_API_URL: envField.string({ context: 'client', access: 'public' }),
      // Solo de servidor, no sensible
      PORT: envField.number({
        context: 'server',
        access: 'public',
        optional: true,
        default: 4321,
      }),
      // Secreta: nunca empaquetada, leída en tiempo de ejecución en el servidor
      CRM_API_KEY: envField.string({ context: 'server', access: 'secret' }),
    },
  },

  security: {
    csp: {
      algorithm: 'SHA-256',
      scriptDirective: {
        // Coincide con la única etiqueta de terceros que el sitio carga realmente
        resources: ["'self'", 'https://cdn.example-analytics.com'],
      },
      styleDirective: {
        resources: ["'self'"],
      },
    },
  },
});
```

```astro
---
// src/components/ContactForm.astro — el valor público, desde el módulo de cliente
import { PUBLIC_API_URL } from 'astro:env/client';
---

<ContactWidget client:visible endpoint={PUBLIC_API_URL} />
```

```ts
// src/pages/api/contact.ts — el secreto se queda en el servidor, por ruta de importación
export const prerender = false;

import { CRM_API_KEY } from 'astro:env/server';

export async function POST({ request }: { request: Request }) {
  const response = await fetch('https://crm.example.com/leads', {
    method: 'POST',
    headers: { authorization: `Bearer ${CRM_API_KEY}` },
    body: await request.text(),
  });

  return new Response(null, { status: response.ok ? 204 : 502 });
}
```

Referencia: [Environment variables](https://docs.astro.build/en/guides/environment-variables/)

### 7.4 Destino de despliegue y mínimo del toolchain

**Impacto (MEDIUM):** Un sitio _Astro_ prerenderizado es un directorio de archivos, y todo el sentido de producirlo en tiempo de compilación es que servirlo no necesita nada más que un _CDN_ — sin servidor de origen, sin arranque en frío, sin runtime que parchear, y con una copia en el centro de datos más cercano a cada visitante. Desplegar esa salida en un servidor de larga duración conserva todos los costes de un servidor y ninguna de sus ventajas. El defecto espejo es un adaptador instalado porque un tutorial lo tenía, que mete al proyecto en silencio en un renderizado bajo demanda que nunca necesitó. El mínimo del toolchain es la otra mitad: la v7 requiere **Node v22.12.0 o superior** y no soporta versiones mayores impares, así que una imagen de _CI_ o un valor por defecto del hosting en una versión antigua o impar falla de una forma que parece un error de código. Declarar la versión en el proyecto es lo que convierte eso en un fallo inmediato y evidente en lugar de uno confuso.

**Directrices:**

1.  **Despliega la salida estática en una plataforma de borde:**
    - _Cloudflare Pages_, _Netlify_ y _Vercel_ compilan y sirven _Astro_ sin configuración, y la salida son archivos
    - La elección entre ellas es operativa — esta regla solo exige que el destino sirva desde una red de borde y no desde un único origen
2.  **El adaptador sigue a la decisión de renderizado, no al revés:**
    - Un sitio totalmente prerenderizado sin rutas bajo demanda y sin islas de servidor no necesita adaptador
    - Instala uno cuando una ruta define `prerender = false`, cuando un componente usa `server:defer`, o cuando las propias funcionalidades de la plataforma lo requieren — y deja que su presencia señale que algo del sitio se renderiza bajo demanda
    - El adaptador y `output` se leen juntos: la regla de salida estática es dueña de qué rutas se renderizan dónde, y esta regla es dueña de dónde se sirve el resultado
3.  **Declara las expectativas de la plataforma dentro del proyecto:**
    - `engines.node` en `package.json`, y la misma versión en la configuración de _CI_ y en los ajustes de compilación del hosting — tres lugares que si no divergirán
    - Solo versiones mayores pares; v22.12.0 es el mínimo actual
    - Fija también la versión del gestor de paquetes allí donde el hosting la respete, para que una compilación local y una de despliegue resuelvan el mismo árbol
4.  **Compila como compila la plataforma:**
    - Ejecuta `astro build` en _CI_ con la misma versión de _Node_ que usa el hosting, y trata una compilación local sin advertencias en otra versión mayor como no verificada
    - `astro check` en la misma cadena captura los errores de tipos y de plantilla que una compilación por sí sola puede dejar pasar
5.  **Mantén revisable la salida del despliegue:**
    - La compilación emite `dist/`; ahí no debería editarse nada, y nada generado debería commitearse
    - Cuando un hosting necesita cabeceras, redirecciones o un archivo de enrutado, genéralo desde la configuración — el mapa de redirecciones ya vive en `astro.config.mjs`

**Incorrecto (un adaptador y un servidor para una salida enteramente estática, versiones sin declarar):**

```json
{
  "name": "example-site",
  "scripts": {
    "build": "astro build",
    "start": "node ./dist/server/entry.mjs"
  }
}
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  site: 'https://example.com',
  // Mal: todas las páginas son estáticas, y las está sirviendo un proceso Node
  // de larga duración que hay que desplegar, monitorizar y parchear
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

**Correcto (salida estática a un CDN de borde, versiones fijadas):**

```json
{
  "name": "example-site",
  "engines": {
    "node": ">=22.12.0"
  },
  "packageManager": "yarn@4.5.0",
  "scripts": {
    "build": "astro check && astro build",
    "preview": "astro preview"
  }
}
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',
  // Salida prerenderizada, servida como archivos desde el borde. Sin adaptador,
  // porque ninguna ruta de este sitio se renderiza bajo demanda
  output: 'static',
});
```

```yaml
# .github/workflows/deploy.yml — el mismo mínimo que usa el hosting
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22.12.0'
      - run: yarn install --immutable
      - run: yarn build
```

Referencia: [Deploy your Astro site](https://docs.astro.build/en/guides/deploy/)
