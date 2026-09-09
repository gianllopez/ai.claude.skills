---
title: Destino de despliegue y mínimo del toolchain
impact: MEDIUM
description: Publica la salida prerenderizada en un CDN de borde con el adaptador y el modo de salida declarados explícitamente, y fija las versiones de Node y del toolchain contra las que el proyecto realmente se construye.
tags: deployment, adapter, cdn, node, toolchain
---

## Destino de despliegue y mínimo del toolchain

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
