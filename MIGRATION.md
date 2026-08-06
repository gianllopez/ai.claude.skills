# Plan de migración — dos skills autoexplicativas

Estado: propuesta, sin ejecutar.

**Decisión.** No hay paquete de núcleo compartido. Cada skill queda completa y autocontenida en su tecnología: quien la carga entiende las directrices sin saltar a otro documento y sin leer ejemplos de una plataforma que no está usando. Las reglas que aplican a ambas se escriben **dos veces, cada una en su idioma** — `onClick` / `onPress`, `ComponentProps<'button'>` / `ComponentProps<typeof Pressable>`, `<ul>` / `<FlatList>`.

El precio de esa decisión es la deriva, y la sección 4 existe para contenerla.

| Skill | Antes | Después | Rol |
| :-- | --: | --: | :-- |
| `react-best-practices` | 26 | **28** | React sobre el DOM: HTML semántico, TailwindCSS v4, shadcn/ui, CLS |
| `react-native-with-expo-best-practices` | 8 | **19** | React sobre RN: NativeWind, Expo Router, config nativa, base/presets |

> **Ya ejecutado.** `arch-components-structure` existe en ambas skills: el patrón base/presets es de React, no de RN. Los archivos de `presets/` perdieron el prefijo del componente padre (`text.tsx`, no `button-text.tsx`), y la versión web fija además el límite con `cva` — variación de estilo es una matriz de variantes, variación de estructura es base/presets.

Ninguna skill depende de la otra. Ningún nombre de skill cambia.

---

## 1. `react-best-practices` — qué cambia

Las 26 reglas actuales se conservan. Se añaden 2 y se corrige 1.

### 1.1 Reglas nuevas (portadas desde RN, en idioma web)

**`arch-typing-system`** (HIGH) — hoy solo existe en la skill de RN, y es contenido que la web necesita igual.

- `core/types/` (dominio) vs `core/typings/` (augmentaciones de librerías)
- Agrupación por dominio con `index.ts` por carpeta
- `import type` / `export type` explícitos
- `interface` para formas de objeto, `type` para uniones e intersecciones
- Sin prefijo `I` en interfaces
- Cierra el hueco de `arch-folder-structure`, que menciona `core/types/` y nunca nombra `core/typings/`

**`arch-core-utilities`** (MEDIUM) — portada y **podada**.

- Se conserva: helpers como exports funcionales, prohibido `class` con métodos `static` (tree-shaking); constantes centralizadas en `core/config/` contra magic strings
- Se descarta por duplicación con `arch-folder-structure`: dónde viven `hooks/`, `lib/`, y la distinción `lib/` vs `helpers/`
- Se descarta por ser de RN: el bloque de tema (`colors.ts`) — en web esa decisión ya la gobierna `tw-theme-tokens`

### 1.2 Corrección

**`data-query-layer`** — los ejemplos usan `protected: true` en cada llamada de axios pero nunca muestran qué lo hace válido. Falta el módulo de augmentación:

```ts
// ./app/core/typings/axios.d.ts
declare module 'axios' {
  export interface AxiosRequestConfig {
    protected?: boolean;
  }
}
```

La skill de RN sí lo trae. Se porta, y se referencia desde `arch-typing-system` como el ejemplo canónico de `core/typings/`.

---

## 2. `react-native-with-expo-best-practices` — qué cambia

Es el grueso del trabajo: 8 reglas a revisar y 11 a escribir.

### 2.1 Contradicciones internas a corregir

**Carpetas declaradas tres veces.** `arch-folder-structure` lista `core/store/` y `core/utils/`; `arch-core-utilities` pone los stores en `core/hooks/stores/` y los helpers en `core/helpers/`.
→ Gana `core/hooks/stores/` + `core/helpers/`, declarado una sola vez en `arch-folder-structure`.

**`export default` prohibido pero exigido.** `arch-components-structure` lo prohíbe sin excepciones; el ejemplo _Correct_ de `arch-folder-structure` usa `export default function Screen()`, y Expo Router lo **exige** en archivos de ruta.
→ Excepción explícita: el router define la convención de export de sus propios módulos de ruta.

**Taxonomía triple de secciones.** El `SKILL.md` tiene una tabla de 2 categorías, un Quick Reference de 4 secciones con unos nombres, y `_sections.md` otras 4 con nombres distintos — que son las que terminan en `AGENTS.md`. Además la tabla marca `arch-` como CRITICAL y ninguna regla `arch-` lo es.
→ Se reescribe `_sections.md` con la estructura final y el `SKILL.md` se deriva de él.

**Falta `shared/`.** El problema que resuelve (el envoltorio de paginación, las formas que ningún dominio posee) existe igual en RN.
→ Se adopta, alineado con la web.

### 2.2 Reglas existentes a mejorar

| Regla | Acción |
| :-- | :-- |
| `arch-api-data-layer` | **Renombrar a `data-query-layer`** (paridad). Corregir el orden de tipos a `Variables → Response → Data`. Añadir lo que le falta frente a la web: `getKey()` para invalidar, middlewares en `core/lib/react-query/`, paralelo vs. cascada con `enabled`, `keepPreviousData`, y la ruta protegida con `<Redirect>` de expo-router en vez de un efecto que navega |
| `arch-syntax-conventions` | Subir al nivel de la web **en idioma RN**: el índice se llama `index` y no `i`; JSX no es excepción; literales de objeto además de tipos; `function` solo para componentes y hooks, con la excepción de hoisting; sin líneas en blanco entre hermanos JSX. La sección de handlers conserva `onPress` / `onChangeText` |
| `arch-style-nativewind` | Quitar `classnames`, adoptar `cn()`. Absorber el bloque de tema (`core/config/theme/colors.ts`) que venía de `arch-core-utilities`. Se le desprende la composición de clases a una regla propia (ver 2.3) |
| `arch-components-structure` | Quitar lo que ahora dictan `arch-syntax-conventions` y `arch-typing-conventions` (declaraciones `function`, named exports, `type Props`), y renombrar el título a `Component File Structure` para converger con la web. La regla de nombres de `presets/` y la justificación del `render` prop **ya están hechas** |
| `arch-folder-structure` | Aplicar las correcciones de 2.1 |
| `arch-typing-system` | Sin cambios de fondo; alinear el ejemplo de `axios.d.ts` con la versión web |
| `arch-core-utilities` | Ceder el bloque de tema a `arch-style-nativewind` |
| `conf-expo` | Sin cambios |

### 2.3 Reglas nuevas (11)

Portadas desde la web y **reescritas en idioma RN**. No es copiar y cambiar el nombre del elemento: varias tienen un ángulo propio que solo aparece en RN, señalado abajo.

| Regla | Impacto | Ángulo propio de RN |
| :-- | :-- | :-- |
| `state-effect-discipline` | CRITICAL | El efecto legítimo cambia: `AppState`, `Linking`, `Keyboard`, listeners de navegación |
| `state-derived-values` | HIGH | — |
| `state-colocation` | HIGH | `useLocalSearchParams` + `router.setParams` en vez de `useSearchParams`. Qué sobrevive a un reload significa otra cosa: deep links y restauración de estado |
| `state-identity-and-keys` | HIGH | `keyExtractor` de `FlatList`, no solo `key`. El defecto se manifiesta al reciclar celdas |
| `data-async-states` | HIGH | `ListEmptyComponent` de `FlatList` es la rama vacía idiomática; `RefreshControl` para el refetch |
| `arch-composition-patterns` | HIGH | — |
| `arch-component-extraction` | HIGH | `cva` funciona igual; el umbral no cambia |
| `arch-typing-conventions` | HIGH | `ComponentProps<typeof Pressable>` en vez de `ComponentProps<'button'>` |
| `arch-markup-minimalism` | HIGH | Wrappers `View`; `gap` en el contenedor. Sin colapso de márgenes en RN — ese argumento se cae y hay que reescribirlo |
| `perf-render-stability` | MEDIUM | Selectores de `zustand` y React Compiler aplican igual |
| `arch-class-composition` | CRITICAL | Desprendida de `arch-style-nativewind`: nunca interpolar clases (NativeWind también escanea texto plano), `cn()` con merge, componentes reutilizables aceptan `className` |

**Fuera de alcance de esta migración**, anotadas como trabajo posterior: un análogo RN de `perf-layout-stability` (rendimiento de `FlatList`: `getItemLayout`, `windowSize`, dimensionado de imágenes) y el protocolo de review que hoy solo tiene el `SKILL.md` de la web. Son contenido nuevo, no portes.

---

## 3. Resolución de los conflictos entre skills

| #   | Conflicto | Resolución |
| --: | :-- | :-- |
| 1 | Orden de tipos: `Response→Data→Variables` (RN) vs `Variables→Response→Data` (web) | Gana web — tiene justificación explícita: sigue la dirección del request |
| 2 | `classnames` (RN) vs `cn()` = `clsx` + `tailwind-merge` (web) | Gana `cn()`. **Verificar primero** el riesgo de la sección 7 |
| 3 | Carpetas RN triplicadas | `core/hooks/stores/` + `core/helpers/` |
| 4 | `export default` | Excepción para módulos de ruta |
| 5 | Taxonomía triple en RN | Se reescribe `_sections.md` y el `SKILL.md` se deriva |
| 6 | Alias `@/` (RN) vs `~/` (web) | **Cada skill declara el suyo y no menciona el otro.** Es exactamente el tipo de mezcla que esta arquitectura evita |

---

## 4. Protocolo anti-deriva

Sin fuente única, 15 de las 46 reglas van a existir por duplicado. `arch-syntax-conventions` ya demuestra el problema: hoy está en ambas skills y la versión web le sacó tres secciones de ventaja sin que nada lo señalara. El objetivo no es impedir que diverjan — a veces deben — sino que la divergencia sea **visible y diffeable** en vez de silenciosa.

**Tres convenciones:**

1. **Nombre de archivo idéntico** cuando expresan el mismo principio. Permite `diff` directo entre las dos carpetas `rules/`
2. **`title` e `impact` idénticos** en el frontmatter. La `description` puede diferir, porque nombra el idioma de la plataforma
3. **La lista de `**Guidelines:**` es el contrato**: mismo número de puntos y mismo orden en ambas versiones. Los ejemplos divergen libremente; las directrices no. Si una plataforma necesita un punto que la otra no tiene, se añade en ambas y en la que no aplica se dice por qué

**Mecanismo:** un campo `pair:` en el frontmatter que nombre a la otra skill, para que la relación sea greppable y el compilador de `AGENTS.md` pueda verificarla.

```yaml
---
title: Effect Discipline
impact: CRITICAL
pair: react-best-practices
---
```

### Tabla de paridad — 15 pares

| Archivo | `react-best-practices` | `react-native-with-expo-…` |
| :-- | :-: | :-: |
| `state-effect-discipline.md` | existe | **nueva** |
| `state-derived-values.md` | existe | **nueva** |
| `state-colocation.md` | existe | **nueva** |
| `state-identity-and-keys.md` | existe | **nueva** |
| `data-query-layer.md` | existe | renombrada |
| `data-async-states.md` | existe | **nueva** |
| `arch-composition-patterns.md` | existe | **nueva** |
| `arch-component-extraction.md` | existe | **nueva** |
| `arch-typing-conventions.md` | existe | **nueva** |
| `arch-markup-minimalism.md` | existe | **nueva** |
| `perf-render-stability.md` | existe | **nueva** |
| `arch-syntax-conventions.md` | existe | alinear |
| `arch-folder-structure.md` | existe | alinear |
| `arch-components-structure.md` | ✅ creada | ✅ actualizada |
| `arch-typing-system.md` | **nueva** | existe |
| `arch-core-utilities.md` | **nueva** | existe |

**Solo en web (12):** `sem-*` (4), `tw-*` (6), `perf-layout-stability`, `perf-css-footprint`

**Solo en RN (3):** `arch-style-nativewind`, `arch-class-composition`, `conf-expo`

16 + 12 = 28 · 16 + 3 = 19 ✓

El par de `arch-components-structure` queda desalineado a propósito hasta la tanda A: la versión de RN todavía carga las directrices de sintaxis y tipado que van a salir de ahí, y por eso conserva el título `Component Structure & Composition` frente al `Component File Structure` de la web. Al ejecutar A los dos títulos y las dos listas de `Guidelines` convergen.

---

## 5. Cambios de contenido pendientes

Los TODOs del `.gitignore` que caen sobre reglas que esta migración va a tocar de todos modos. Conviene resolverlos **durante**, no antes ni después.

| TODO | Dónde cae | Naturaleza |
| :-- | :-- | :-- |
| "Verificar que reglas de RN deben ir en `react-best-practices` y heredar" | — | **Resuelto por este plan**: no heredan, se duplican en su idioma. Se puede borrar |
| "Que solo se aplique `handle*` cuando valga la pena; para una sola llamada no tiene sentido" | `arch-syntax-conventions`, en **ambas** | Cambio de fondo. Hoy la regla no admite excepción |
| "Que solo sean obligatorios `isPending`/`isError`/`isEmpty` donde valga la pena" | `data-async-states`, en **ambas** | Cambio de fondo. **Contradice la regla actual**, que exige las cuatro ramas siempre |
| "Cambiar la premisa de 'own pure functions, with no third-party dependency'" | `arch-folder-structure` (web) y por paridad RN | Ajuste de una guideline |
| ~~"Que en componentes base/presets los presets no lleven el prefijo del padre"~~ | `arch-components-structure`, en ambas | ✅ **Resuelto.** Base/presets es de React: la regla existe en las dos skills y los archivos de `presets/` perdieron el prefijo. Se puede borrar del `.gitignore` |
| "Agregar una regla a RN para configuración y despliegue" | Nueva, junto a `conf-expo` | Contenido nuevo. Subiría RN a 20 |

---

## 6. Orden de trabajo

1. **Verificar `tailwind-merge` bajo NativeWind.** Bloquea el conflicto #2. Si no es viable, `arch-class-composition` de RN admite otro helper y lo dice explícitamente
2. **Web:** añadir las 2 reglas, corregir `data-query-layer`, registrar en `_sections.md`, recompilar `AGENTS.md`
3. **RN:** corregir las contradicciones internas y mejorar las 8 existentes, incluido el renombrado a `data-query-layer`
4. **RN:** reescribir `_sections.md` y derivar el `SKILL.md` de él
5. **RN:** escribir las 11 nuevas en idioma RN — es el bloque de trabajo real, no un copiar y pegar
6. **Ambas:** añadir el campo `pair:` y la tabla de paridad al `README.md` de cada una
7. **Ambas:** recompilar `AGENTS.md` siguiendo `skill-factory/references/compilation.md`
8. **Ambas:** actualizar `metadata.json` — `abstract`, `references`, `version`

---

## 7. Riesgos

| Riesgo | Mitigación |
| :-- | :-- |
| **Deriva entre las 15 reglas pareadas** — el riesgo principal de esta arquitectura | El protocolo de la sección 4. No lo elimina; lo hace detectable |
| `tailwind-merge` puede no comportarse bajo NativeWind | Verificar en el paso 1 antes de escribir la regla como obligatoria |
| El `AGENTS.md` de RN pasa de 843 líneas a ~2.500 | Revisar que siga siendo utilizable como artefacto único; si no, es la señal para dividirlo por secciones |
| Las 11 reglas nuevas no son un porte mecánico | Cada una necesita ejemplos RN que se sostengan: `FlatList`, `Pressable`, expo-router. Presupuestar como escritura, no como copia |
| Este documento está en español; el resto del repo, en inglés | Decidir si se traduce antes de darlo por bueno |
