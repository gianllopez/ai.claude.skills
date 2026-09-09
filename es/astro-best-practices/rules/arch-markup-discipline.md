---
title: Disciplina de marcado bajo el compilador de la v7
impact: HIGH
description: Exige un marcado bien formado y semánticamente válido ahora que el compilador Rust de la v7 trata las etiquetas sin cerrar como errores de compilación, deja de autocorregir el anidamiento inválido y comprime los espacios en blanco con reglas de JSX.
tags: markup, html, compiler, v7, build
---

## Disciplina de marcado bajo el compilador de la v7

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
