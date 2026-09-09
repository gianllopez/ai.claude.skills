---
title: Entorno tipado y política de seguridad de contenido
impact: HIGH
description: Declara cada variable de entorno en el esquema de astro:env para que los secretos no puedan llegar al bundle del cliente, y activa la política de seguridad de contenido integrada en lugar de publicar sin ninguna.
tags: environment, secrets, security, csp, configuration
---

## Entorno tipado y política de seguridad de contenido

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
