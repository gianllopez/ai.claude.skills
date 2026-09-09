---
title: Registro estructurado de la compilación
impact: LOW
description: Usa Astro.logger para los diagnósticos de tiempo de compilación y configura el manejador logger estable de nivel superior, en lugar de líneas console.log que no llevan nivel ni contexto.
tags: logging, build, diagnostics, configuration
---

## Registro estructurado de la compilación

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
