# Buenas prácticas de Astro

Un repositorio estructurado de buenas prácticas de _Astro_, optimizado para agentes, LLMs y personas que desarrollan. La versión de referencia es **Astro 7**.

## Estructura

- `SKILL.md` - Qué gobierna la skill, cuándo aplicarla y la referencia rápida
- `rules/` - Archivos de regla individuales (uno por regla)
  - `_sections.md` - Índice de todas las reglas, agrupadas por sección
  - `_template.md` - Plantilla para crear reglas nuevas
  - `<prefijo>-<nombre>.md` - Definiciones de reglas individuales
- `metadata.json` - Metadatos del documento (versión, autor, resumen, enlaces de referencia)
- `AGENTS.md` - Salida compilada generada (todas las reglas expandidas). Nunca se edita a mano

## Alcance

Esta skill es dueña del framework y de lo que emite: el modo de renderizado, las fronteras de isla y la hidratación, el modelo de contenido, el sistema de SEO generado a partir de él, los recursos, la estructura del proyecto, la configuración de estilos y la configuración de compilación.

Dos cosas quedan deliberadamente excluidas:

- **Lo que ocurre dentro de una isla de framework.** Un proyecto que renderiza islas de _React_ carga `react-core-best-practices` junto a esta skill, que es dueña de los efectos, el estado, la capa de consultas, la composición y el tipado. Esta skill es dueña solo de si la isla debe existir y de cómo se hidrata
- **La dirección de diseño visual y la auditoría de accesibilidad.** Ninguna de las dos es verificable contra un diff, que es el listón que cumple cada regla de aquí. La guía semántica y estructural se justifica en su lugar por legibilidad para máquinas y mantenibilidad — la misma decisión que toma `react-best-practices`

## Categorías de reglas

| Prioridad | Categoría                   | Impacto máximo | Prefijo    | Reglas |
| :-------- | :-------------------------- | :------------- | :--------- | -----: |
| 1         | Renderizado e hidratación   | CRITICAL       | `isl-`     |      3 |
| 2         | Modelo de contenido         | CRITICAL       | `content-` |      3 |
| 3         | Sistema de SEO              | CRITICAL       | `seo-`     |      4 |
| 4         | Recursos y rendimiento      | HIGH           | `perf-`    |      4 |
| 5         | Estructura del proyecto     | HIGH           | `arch-`    |      4 |
| 6         | Estilos                     | HIGH           | `style-`   |      2 |
| 7         | Compilación y configuración | HIGH           | `build-`   |      4 |

## Cómo usar la skill

Lee `SKILL.md` para la visión general y la referencia rápida, y después los archivos de regla individuales para la justificación completa y los ejemplos. `AGENTS.md` es ese mismo contenido como un único documento distribuible.

Cada regla está escrita para poder usarse en ambas direcciones: el bloque **Correcto** es lo que hay que escribir, y el bloque **Incorrecto** es el defecto que hay que buscar en un diff.

## Manejo de versiones

Las versiones mayores recientes de _Astro_ eliminaron APIs reales — `Astro.glob()`, las colecciones de contenido heredadas, `<ViewTransitions />`, `@astrojs/db` — así que una guía escrita contra una versión anterior no solo envejece, deja de funcionar. Dos convenciones mantienen esto sostenible:

- Cada regla que nombra una clave de configuración, una ruta de importación o un componente declara la versión a la que pertenece
- Cuando la intención de una regla sobrevive a su API, se enuncia primero la intención y después la API

Cuando salga una nueva versión mayor, las reglas que hay que verificar primero son aquellas cuyos ejemplos contienen configuración: `isl-static-by-default`, `content-collections-required`, `content-authoring-format`, `build-env-and-csp`, `build-logging` y `build-deployment-target`.

## Flujo de trabajo

1. **Define reglas:** crea o edita archivos markdown en `rules/`
2. **Regenera:** reconstruye `AGENTS.md` a partir de las reglas (ver más abajo). Es un artefacto generado — edita las reglas, no `AGENTS.md`
3. **Formatea:** ejecuta `prettier --write` sobre cada archivo modificado
4. **Distribuye:** reparte `AGENTS.md`

## Crear una regla nueva

1. Copia `rules/_template.md` a `rules/<prefijo>-<nombre>.md`
2. Elige el prefijo de categoría de la tabla de arriba
3. Rellena el frontmatter (`title`, `impact`, `description`, `tags`)
4. Aporta ejemplos claros de _Incorrecto_ frente a _Correcto_, y verifica contra la documentación actual cualquier API que nombres en ellos
5. Registra la regla en `rules/_sections.md` (sección + orden)
6. Regenera `AGENTS.md`

## Regenerar `AGENTS.md`

No hay script de compilación. `AGENTS.md` se regenera siguiendo el procedimiento descrito en `skill-factory/SKILL.md` (_AGENTS.md Compilation_) — leyendo `rules/`, `rules/_sections.md` y `metadata.json`, y produciendo después el documento compilado. Las fuentes de verdad son las reglas y `metadata.json`.

## Agradecimientos

Estructura adaptada de [agent-skills de Vercel Labs](https://github.com/vercel-labs/agent-skills).
