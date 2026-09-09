---
title: Salida estática por defecto
impact: CRITICAL
description: Exige el renderizado en tiempo de compilación como valor por defecto del proyecto y el renderizado bajo demanda como una excepción por ruta que nombra los datos de tiempo de solicitud que necesita.
tags: rendering, output, prerender, adapter
---

## Salida estática por defecto

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
