---
title: Alias de rutas de TypeScript
impact: LOW
description: Declara alias de importación en tsconfig.json para que los módulos se referencien por su lugar en el proyecto y no por una ruta relativa que se rompe cuando un archivo se mueve.
tags: typescript, imports, configuration, structure
---

## Alias de rutas de TypeScript

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
