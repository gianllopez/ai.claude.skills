---
name: skill-factory
description: Guía y plantillas para crear nuevas Agent Skills en esta colección. Úsala al crear una skill nueva, montar el andamiaje de su estructura de carpetas, decidir el nivel de complejidad de una skill, estandarizar una skill existente, o configurar el procedimiento de compilación de rules/AGENTS.md. Se activa con "crear una skill", "nueva skill", "andamiaje de una skill", "estructura de skill", "nivel de skill".
license: MIT
metadata:
  author: gianllopez
  version: 2.0.0
---

# Skill Factory

Estándar de autoría para las skills de esta colección. Define tres niveles de complejidad, los formatos exactos de archivo que usa cada nivel, y el procedimiento de compilación para las skills basadas en reglas — de modo que cada skill sea organizada, escalable y consistente.

## Cuándo aplicarla

- Al crear una skill completamente nueva desde cero
- Al elegir la estructura de carpetas adecuada para la complejidad de una skill
- Al estandarizar o promocionar una skill existente (p. ej., promover una skill procedimental que crece a una compilada)
- Al configurar o regenerar el `AGENTS.md` de una skill basada en reglas

## Qué se requiere realmente

Según la [especificación oficial de Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), una skill solo necesita un `SKILL.md` con frontmatter _YAML_ (`name` + `description`). Todo lo demás (`metadata.json`, `README.md`, `rules/`, `AGENTS.md`) es una convención que esta colección adopta — adaptada de [agent-skills de Vercel Labs](https://github.com/vercel-labs/agent-skills) — para mantener manejables las skills grandes. Los niveles de abajo superponen esa convención sobre la especificación según la complejidad.

## Elige un nivel

| Nivel             | Úsalo cuando…                                                                                                                | Archivos                                                                         | Ejemplos                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 1 · Mínimo        | Una instrucción o procedimiento estable, sin recursos, sin versionado                                                        | `SKILL.md`                                                                       | `commit`                                                                        |
| 2 · Procedimental | Un flujo de trabajo o integración con una herramienta; puede incluir scripts auxiliares; se beneficia de versionado + README | `SKILL.md`, `metadata.json`, `README.md`, opcionalmente `scripts/`, `templates/` | `notion`, `audit`, `review`, `skill-factory`                                    |
| 3 · Compilado     | Un catálogo grande y en evolución de muchas reglas independientes distribuido como un único documento compilado              | Nivel 2 **+** `rules/` **+** `AGENTS.md` (generado)                              | `django-rest-framework-best-practices`, `react-native-with-expo-best-practices` |

**Heurística:** una instrucción → _Nivel 1_ · un flujo de trabajo o herramienta → _Nivel 2_ · muchas reglas que necesitan un único artefacto distribuible → _Nivel 3_.

```
¿Es una instrucción estable sin recursos?                        → Nivel 1
¿Es un flujo de trabajo o herramienta (quizá con un script)?     → Nivel 2
¿Son muchas reglas independientes → un documento compilado?      → Nivel 3
```

La estructura de carpetas de una skill debería corresponder a su complejidad — ni más, ni menos. Añadir `rules/` y un `AGENTS.md` compilado a un procedimiento de una línea es sobrecarga; embutir un catálogo grande de reglas en un único `SKILL.md` es inmantenible. Elige el nivel más pequeño que encaje, y en caso de duda empieza un nivel por debajo — promocionar después es copiar y dividir, no reescribir.

### Nivel 1 · Mínimo

Úsalo cuando la skill es una única instrucción o procedimiento estable, sin recursos de apoyo, sin código ejecutable auxiliar y sin necesidad de versionado ni changelog. Todo cabe cómodamente en `SKILL.md` (mantén el cuerpo por debajo de unos 5k tokens).

```
<skill-name>/
└── SKILL.md
```

**Ejemplo:** `commit` — un procedimiento (analizar los cambios en staging, escribir un _Conventional Commit_).

**Promociona al Nivel 2 cuando** empieces a querer un script auxiliar, recursos incluidos o metadatos de versión.

### Nivel 2 · Procedimental

Úsalo cuando la skill codifica un flujo de trabajo o una integración con una herramienta o _API_. Puede incluir scripts auxiliares (código ejecutable de nivel 3), y se beneficia de metadatos de versión y de un `README.md` dirigido a personas.

```
<skill-name>/
├── SKILL.md          # todo el procedimiento + cuándo usarla
├── metadata.json     # versión, autor, resumen, enlaces de referencia
├── README.md         # visión general para personas
├── scripts/          # opcional: auxiliares ejecutables (se ejecutan vía bash)
│   └── <tool>.py
└── templates/        # opcional: recursos listos para copiar que la skill entrega
```

**Ejemplos:** `notion` (flujo de trabajo sobre una _API_), `audit` (auxiliar `scripts/audit.py`), `review` (tres archivos, nada más), y la propia `skill-factory` (incluye `templates/`).

**Todo vive en `SKILL.md`.** Una skill de _Nivel 2_ nunca reparte sus instrucciones entre documentos laterales — el procedimiento completo se queda en `SKILL.md` para que una sola lectura dé la imagen entera. Varios cientos de líneas es normal; `notion` y `review` están ahí. Prefiere un auxiliar en `scripts/` antes que prosa cuando una operación deba ser determinista.

**Promociona al Nivel 3 cuando** el cuerpo deje de ser un procedimiento coherente y se convierta en un catálogo grande de muchas directrices independientes que quieras distribuir como un único documento compilado. Que `SKILL.md` se quede pequeño es una señal para promocionar, nunca para dividir el archivo.

### Nivel 3 · Compilado (best-practices)

Úsalo cuando la skill es un conjunto grande y en evolución de muchas reglas independientes que (a) se benefician de la modularidad de una regla por archivo y (b) se consumen como un único artefacto compilado (`AGENTS.md`).

```
<skill-name>/
├── SKILL.md               # visión general, cuándo aplicarla, referencia rápida
├── metadata.json          # versión, autor, resumen, enlaces de referencia
├── README.md              # visión general para personas + flujo de autoría
├── rules/
│   ├── _sections.md       # índice de todas las reglas, agrupadas por sección
│   ├── _template.md       # andamiaje de regla en blanco
│   └── <prefix>-<name>.md # una regla por archivo
└── AGENTS.md              # GENERADO: todas las reglas compiladas en un documento
```

- Los nombres de archivo de las reglas usan un prefijo de categoría (p. ej. `arch-`, `conf-`) para que se ordenen y agrupen por área
- `AGENTS.md` es un artefacto generado — nunca se edita a mano. Se regenera siguiendo el procedimiento de _AGENTS.md Compilation_ más abajo (leyendo las reglas y `metadata.json`), no mediante ningún script incluido

**Ejemplos:** `django-rest-framework-best-practices`, `react-native-with-expo-best-practices`.

## Flujo de autoría

1. **Elige un nivel** usando la tabla de arriba
2. **Usa el nombre que eligió el usuario** — nunca lo inventes ni lo elijas tú; si falta, pregunta. Después valídalo: solo letras minúsculas, números y guiones; ≤ 64 caracteres; no debe contener `anthropic` ni `claude`
3. **Copia la plantilla correspondiente** de `templates/tier-<n>/` a `~/.claude/skills/<skill-name>/`
4. **Rellena todos los marcadores** (`<skill-name>`, `<Title>`, `<description>`, …). La `description` debe indicar qué hace la skill y cuándo usarla — es el texto contra el que _Claude_ hace la correspondencia
5. **Solo Nivel 3:** escribe una regla por archivo bajo `rules/`, registra cada una en `rules/_sections.md`, y después compila `AGENTS.md` siguiendo _AGENTS.md Compilation_ más abajo
6. **Verifica** contra las listas de comprobación de _File Formats_ más abajo

## Formatos de archivo

Formatos exactos y listas de comprobación para cada archivo que una skill puede contener. Copia la plantilla correspondiente de `templates/` y valida después contra la lista de comprobación de aquí.

### Convenciones de prosa

Aplícalas en todos los archivos markdown de una skill:

- Escribe en _inglés_
- Pon en cursiva los nombres propios y de producto en la prosa (`_Django_`, `_Docker_`); déjalos sin formato en encabezados, código, texto de enlace y frontmatter
- No termines los elementos de una enumeración (viñeta, numerada o lista de comprobación) con punto; conserva los puntos solo dentro de los párrafos de prosa corrida
- Mantén los artefactos generados (`AGENTS.md`) fuera de las ediciones manuales

### `SKILL.md` (todos los niveles — obligatorio)

El único archivo que la especificación oficial exige. Frontmatter _YAML_ + un cuerpo en markdown.

```markdown
---
name: <skill-name>
description: <qué hace Y cuándo usarla; palabras que la activan>
license: MIT # opcional (convención de Nivel 2/3)
metadata: # opcional (convención de Nivel 2/3)
  author: <handle>
  version: <x.y.z>
---

# <Título>

<Cuerpo: instrucciones, cuándo aplicarla, referencia rápida>
```

**Reglas del frontmatter (las impone la plataforma):**

- `name`: lo elige el usuario (nunca se genera) · solo letras minúsculas, números y guiones · ≤ 64 caracteres · sin etiquetas _XML_ · no debe contener `anthropic` ni `claude`
- `description`: no vacía · ≤ 1024 caracteres · sin etiquetas _XML_ · debe decir qué hace la skill y cuándo debería usarla _Claude_ (este es el texto contra el que _Claude_ hace la correspondencia)

**Lista de comprobación:**

- [ ] `name` coincide con el nombre de la carpeta
- [ ] `description` incluye tanto la capacidad como las condiciones que la activan
- [ ] El cuerpo es autocontenido — todo el procedimiento vive aquí, nunca repartido en documentos laterales
- [ ] Escrito en _inglés_ (convención de la colección)

### `metadata.json` (Nivel 2/3)

Metadatos para personas y herramientas. La plataforma no lo lee; es la fuente única para el encabezado del `AGENTS.md` compilado en el _Nivel 3_. Su campo `references` es una lista de _URLs_ externas — el material de origen en el que se basa la skill.

```json
{
  "version": "1.0.0",
  "author": "<Nombre>",
  "date": "<Mes Año>",
  "abstract": "<resumen de 1 a 3 frases sobre alcance e intención>",
  "references": ["<url>", "..."]
}
```

**Lista de comprobación:**

- [ ] `version` coincide con el `metadata.version` del frontmatter de `SKILL.md`
- [ ] `date` es absoluta (`Mes Año`), no relativa
- [ ] `abstract` describe alcance e intención, no detalles triviales de implementación

### `README.md` (Nivel 2/3)

Visión general dirigida a personas. Describe el propósito de la skill, su estructura de archivos y cómo usarla o mantenerla. Para el _Nivel 3_ documenta además el flujo de autoría (crear una regla, recompilar).

**Lista de comprobación:**

- [ ] Lista la estructura de archivos con descripciones de una línea
- [ ] Indica cómo usar la skill
- [ ] Nivel 3: documenta los pasos de "crear una regla" y "recompilar `AGENTS.md`" y marca `AGENTS.md` como generado

### `rules/` (Nivel 3)

#### `rules/_sections.md`

Índice de todas las reglas, agrupadas por sección, enlazando cada archivo de regla. Mantenlo sincronizado con el conjunto real de reglas y con el orden de secciones usado para compilar `AGENTS.md`.

#### `rules/_template.md`

Un andamiaje de regla en blanco que se copia al escribir una nueva. Establece la forma estricta de una regla.

#### `rules/<prefix>-<name>.md`

Una regla por archivo. Los nombres de archivo empiezan con un prefijo de categoría (`arch-`, `conf-`, …) para que las reglas relacionadas se ordenen juntas.

````markdown
---
title: <Título>
impact: <CRITICAL | HIGH | MEDIUM | LOW>
description: <resumen de una línea>
tags: <separadas, por, comas>
---

## <Título>

**Impacto (<NIVEL>):** <por qué importa>

**Directrices:** <lista numerada opcional>

**Incorrecto (<qué está mal>):**

```<lang>
<mal ejemplo>
```

**Correcto (<qué está bien>):**

```<lang>
<buen ejemplo>
```

Referencia: [<etiqueta>](url)
````

**Lista de comprobación por regla:**

- [ ] Nombre de archivo `<prefix>-<name>.md`; el primer encabezado es `## <Título>`
- [ ] El frontmatter tiene `title`, `impact`, `description`, `tags`
- [ ] Tiene ejemplos claros de _Incorrecto_ y _Correcto_
- [ ] Está registrada en `rules/_sections.md`
- [ ] Nombres propios y de producto en cursiva en la prosa (`_Django_`, `_Docker_`, …); sin formato en encabezados, código, texto de enlace y frontmatter

### `AGENTS.md` (Nivel 3 — generado)

El documento compilado completo: encabezado al estilo _Vercel_ (título, versión, Nota, Resumen), una tabla de contenidos derivada, y cada regla expandida en línea bajo secciones numeradas. Nunca se edita a mano. El formato exacto y cómo se produce vienen a continuación.

## AGENTS.md Compilation (Nivel 3)

`AGENTS.md` es el documento distribuible único de una skill de _Nivel 3_: cada regla expandida en línea, en un orden fijo, tras un encabezado y una tabla de contenidos derivada. Es un artefacto generado — nunca se edita a mano.

No hay script de compilación ni comando incluido. Tú (el agente) produces `AGENTS.md` leyendo `rules/`, `rules/_sections.md` y `metadata.json` de la skill, y siguiendo después el procedimiento de abajo — la estructura se describe aquí, y el artefacto se crea a partir del análisis de las propias reglas.

### Fuentes de verdad

- **`rules/_sections.md`** — la agrupación y el orden de las secciones, y qué reglas pertenecen a cada una
- **`rules/<slug>.md`** — el título de cada regla (su encabezado `## `), su `impact` (frontmatter) y su cuerpo
- **`metadata.json`** — `version`, `author`, `date`, `abstract` para el encabezado
- **`SKILL.md`** — el título humano de la skill (su encabezado `# ` superior)

### Formato de salida (alineado con Vercel)

```
# <Título de la skill>

**Version <versión>**            ← dos espacios finales = salto de línea duro
_<Autor>_
_<Fecha>_

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring <domain> codebases. Humans
> may also find it useful, but guidance here is optimized for automation
> and consistency by AI-assisted workflows.

---

## Abstract

<resumen de metadata.json>

---

## Table of Contents

1. [<Sección>](#1-section) — `<IMPACT>`
   - [1.1 <Título de la regla>](#11-rule-title)
   ...

---

## 1. <Sección>

### 1.1 <Título de la regla>

<cuerpo de la regla: Impacto, Directrices, Incorrecto/Correcto, Referencia>
...
```

### Procedimiento

#### 1 · Encabezado

Constrúyelo a partir de `metadata.json` y `SKILL.md`; no mantengas un archivo de encabezado aparte:

- `# <Título de la skill>` — el título humano de la skill (el encabezado `# ` de `SKILL.md`)
- `**Version <versión>**` — termina la línea con dos espacios (salto duro)
- `_<autor>_` — en cursiva, salto duro de dos espacios
- `_<fecha>_` — en cursiva
- La cita en bloque de la nota, literal según el formato de arriba, con `<domain>` reemplazado por la tecnología que gobierna la skill (p. ej. "Django and Django REST Framework")
- `---`, después `## Abstract`, después el `abstract` de `metadata.json` (los nombres propios pueden ir en cursiva), después `---`

#### 2 · Tabla de contenidos (derivada)

- Numera las secciones en el orden de `rules/_sections.md` (`N`), y las reglas dentro de cada sección (`N.M`)
- Línea de sección: `N. [<Sección>](#<ancla>) — ` + el impacto más fuerte entre sus reglas entre comillas invertidas (rango `CRITICAL > HIGH > MEDIUM > LOW`)
- Línea de regla (indentada tres espacios): `- [N.M <Título de la regla>](#<ancla>)`
- Ancla = el texto visible del encabezado (incluido su número) en minúsculas, eliminando todo carácter que no sea letra, dígito, espacio o guion, y convirtiendo después los espacios en guiones. Ejemplos: `## 2. Configuration & DevOps` → `#2-configuration--devops`; `### 2.2 Deployment Topology` → `#22-deployment-topology`

#### 3 · Cuerpo (reglas expandidas)

- Para cada sección, en orden: `## N. <Sección>`
- Para cada regla, en orden: `### N.M <Título de la regla>`, seguido del cuerpo de la regla — todo lo que va después de su frontmatter y después de su propia línea de título `## ` — con cualquier encabezado `### ` interno degradado a `#### ` para que anide bajo la regla numerada
- Separa las secciones (y el encabezado de la tabla de contenidos) con una línea `---`

### Invariantes a verificar tras generar

- **Idempotente:** regenerar sin cambios de contenido reproduce el mismo archivo
- **Las anclas resuelven:** cada enlace de la tabla de contenidos coincide con el slug de un encabezado
- **Sin fugas:** en la salida no aparece ningún frontmatter de regla ni ningún título de regla sin numerar
- **Espaciado:** exactamente una línea en blanco después de cada encabezado

### Añadir una regla (resumen)

- Crea `rules/<prefix>-<name>.md` a partir de `rules/_template.md`
- Regístrala en `rules/_sections.md` (sección + orden)
- Regenera `AGENTS.md` siguiendo este procedimiento
