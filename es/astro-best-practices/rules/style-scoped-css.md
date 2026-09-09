---
title: Estilos de componente con ámbito
impact: MEDIUM
description: Mantiene el CSS de un componente dentro de su bloque de estilos con ámbito, reserva is:global para los estilos que deben escapar de él, y pasa los valores dinámicos mediante define:vars en lugar de atributos style en línea.
tags: styling, css, scoped, global, astro
---

## Estilos de componente con ámbito

**Impacto (MEDIUM):** Un bloque `<style>` en un archivo `.astro` queda acotado a ese componente automáticamente, y solo se emiten las reglas que el componente realmente renderiza — así que los estilos de componente no pueden filtrarse, no pueden ser sobrescritos por un archivo sin relación, y no pueden acumularse en una hoja de estilos global de la que nadie se atreve a borrar nada. `is:global` renuncia a las tres cosas de golpe. Es la herramienta correcta para el puñado de cosas que sí son globales — resets, reglas sobre `body`, dar estilo a marcado del que el componente no es dueño, como la salida de _Markdown_ renderizada mediante `<Content />` — y también es la forma más rápida de convertir un sistema con ámbito en el sistema global que reemplazó, porque hace que un selector rebelde funcione al instante. El defecto relacionado es el atributo `style` en línea usado para pasar un valor: se salta la hoja de estilos por completo, así que el valor no puede ser un token, no puede responder a una media query, y no puede sobrescribirse con nada que no sea `!important`.

**Directrices:**

1.  **Primero las utilidades, y estilos con ámbito para lo que las utilidades no pueden expresar:**
    - En un proyecto _TailwindCSS_ la mayor parte del estilo de componente son atributos de clase, y un bloque con ámbito no es una forma de evitarlos
    - Se gana su lugar para keyframes, selectores complejos, reglas `::view-transition`, comportamiento específico de contenedor, y cualquier cosa genuinamente local que como cadena de utilidades sería ruido
2.  **`is:global` nombra su motivo:**
    - Legítimo: resets y reglas base en la hoja de estilos del layout, dar estilo a la salida de `<Content />` que el componente no escribió, marcado de terceros que el componente envuelve
    - No legítimo: hacer que un selector coincida porque el ámbito estorbaba. Si un estilo tiene que alcanzar a un componente hijo, el hijo debería ser su dueño, o el valor debería viajar como prop
    - `:global()` alrededor de un único selector es la herramienta más estrecha cuando solo parte de una regla debe escapar
3.  **Pasa los valores dinámicos con `define:vars`, no con estilos en línea:**
    - `define:vars={{ accent }}` expone un valor del frontmatter al bloque con ámbito como variable _CSS_, de modo que el valor se queda en la hoja de estilos, donde las variantes y las media queries todavía pueden alcanzarlo
    - Un atributo `style` en línea se reserva para valores genuinamente calculados en tiempo de ejecución en el navegador
4.  **Las hojas de estilo globales se mantienen pequeñas y en un solo sitio:**
    - `src/styles/global.css` contiene el import de _Tailwind_, el tema y el puñado de reglas base — no es donde van los estilos de componente
    - Un estilo de componente que se ha promocionado a global porque dos componentes lo necesitaban suele ser un tercer componente esperando a ser extraído
5.  **Da estilo a lo que el componente posee:**
    - Un componente que se mete en las interioridades de un hijo con un selector descendiente crea un acoplamiento que sobrevive a cada refactor del hijo
    - Cuando un padre debe influir en la apariencia de un hijo, el hijo lo expone — una prop, una prop `class` fusionada en su raíz, un atributo de datos desde el que da estilo

**Incorrecto (escapes globales y un valor en línea):**

```astro
---
// src/components/Callout.astro
const { accent } = Astro.props;
---

<div class="callout">
  <!-- Mal: el valor se salta la hoja de estilos, así que ninguna variante ni
       media query puede alcanzarlo -->
  <span class="callout__bar" style={`background: ${accent}`}></span>
  <slot />
</div>

<style is:global>
  /* Mal: global porque un selector no coincidía. Todos los .callout del sitio
     están ahora estilizados por este componente, incluidos los que nunca renderizó */
  .callout {
    border-left: 4px solid;
    padding: 1rem;
  }

  /* Mal: metiéndose en las interioridades de un componente hijo */
  .callout .card__title {
    font-weight: 700;
  }
</style>
```

**Correcto (con ámbito por defecto, variables para los valores dinámicos, global solo donde debe serlo):**

```astro
---
// src/components/Callout.astro
interface Props {
  accent?: string;
}

const { accent = 'var(--color-brand)' } = Astro.props;
---

<div class="callout">
  <span class="callout__bar"></span>
  <slot />
</div>

<!-- Con ámbito: estas reglas no pueden filtrarse, y solo se emite lo que se renderiza -->
<style define:vars={{ accent }}>
  .callout {
    border-left: 4px solid var(--accent);
    padding: 1rem;
  }

  .callout__bar {
    background: var(--accent);
  }
</style>
```

```astro
---
// src/layouts/Article.astro — global, con un motivo: esto da estilo a la salida
// de Markdown que el layout renderiza pero no escribió
import { render } from 'astro:content';

const { Content } = await render(Astro.props.post);
---

<article class="prose">
  <Content />
</article>

<style is:global>
  .prose h2 {
    margin-block-start: 2rem;
  }

  .prose :where(a) {
    text-decoration: underline;
  }
</style>
```

Referencia: [Styling and CSS](https://docs.astro.build/en/guides/styling/)
