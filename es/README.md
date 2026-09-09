# `es/` — copia en español para revisión manual

Esta carpeta **no forma parte de las skills**. Es un espejo en español, generado para facilitar la
revisión manual, de todos los archivos que la base de datos del plugin `audit` marca como `pending`.
Las skills reales siguen escribiéndose en inglés y viven en la raíz del proyecto; nada de aquí se
distribuye ni se carga como skill.

## Qué contiene

La misma estructura de directorios que el proyecto, pero únicamente con los archivos en estado
`pending` en el momento de generarla:

```plaintext
es/
├── astro-best-practices/          # 28 archivos (todo el skill está pending)
│   ├── AGENTS.md
│   ├── README.md
│   ├── SKILL.md
│   ├── metadata.json
│   └── rules/                     # _sections, _template y las 24 reglas
├── django-rest-framework-best-practices/
│   ├── AGENTS.md
│   ├── SKILL.md
│   ├── metadata.json
│   └── rules/
│       └── arch-api-serializer-definition.md
└── skill-factory/
    └── SKILL.md
```

Los archivos con estado `done` **no** están aquí, y sus originales no se han tocado. La única
excepción visible es `django-rest-framework-best-practices/AGENTS.md`: es un archivo `pending` que,
por ser un artefacto compilado, contiene también el texto de reglas que sí están `done`. Se ha
traducido completo porque el archivo en sí es lo que está pendiente de revisión.

## Convenciones de la traducción

Para que la revisión pueda hacerse en paralelo contra el original:

- **Los nombres de archivo no cambian.** Cada archivo de `es/` está en la misma ruta que su original,
  así que la correspondencia es 1:1
- **Se traduce la prosa**, incluidos títulos, descripciones y los comentarios dentro de los bloques
  de código — que es donde vive la explicación
- **No se traduce el código:** identificadores, claves de configuración, rutas de importación,
  nombres de API, cadenas de ejemplo y salidas de terminal se dejan literales
- **Los identificadores técnicos se conservan:** `name` del frontmatter, `tags`, los valores de
  `impact` (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`), los slugs de las reglas y las URLs de referencia. Los
  títulos de los documentos enlazados en `Referencia:` se mantienen en su idioma original
- **Se respetan las convenciones de prosa del proyecto:** nombres propios en cursiva, sin punto final
  en los elementos de enumeración

## Cómo se generó `astro-best-practices/AGENTS.md`

No se tradujo a mano: se compiló desde las reglas ya traducidas siguiendo el procedimiento de
`skill-factory/SKILL.md` (_AGENTS.md Compilation_), con el mismo compilador validado previamente
contra el `AGENTS.md` en inglés, que reproduce byte a byte. Por eso su contenido no puede divergir de
las reglas de `es/astro-best-practices/rules/`.

## Entrada obsoleta

La base de datos de `audit` lista `astro-best-practices.md` (en la raíz) como `pending`, pero ese
archivo ya no existe en el proyecto. No tiene traducción aquí, y conviene limpiar la entrada con el
plugin.
