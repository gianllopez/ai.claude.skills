---
title: Directivas de hidratación y fronteras de isla
impact: CRITICAL
description: Exige que la directiva client:* corresponda a la posición y la prioridad del componente, y que la frontera de la isla envuelva solo lo que realmente es interactivo.
tags: islands, hydration, client-directives, performance
---

## Directivas de hidratación y fronteras de isla

**Impacto (CRITICAL):** Una directiva `client:*` es una orden de compra de _JavaScript_, y la directiva decide cuándo paga el navegador. `client:load` significa que el bundle se solicita y se ejecuta durante la carga inicial de la página, compitiendo con todo lo demás, vea o no el usuario alguna vez el componente; `client:visible` significa que ni siquiera se solicita hasta que el componente entra en pantalla, de modo que un gráfico al final de una página larga le cuesta exactamente nada a quien nunca hace scroll. Las dos se ven idénticas en la revisión e idénticas en la página renderizada — la diferencia solo aparece en la cascada de red, y por eso `client:load` se propaga: es la que siempre funciona, así que se convierte en la que siempre se usa. La segunda mitad del defecto es la frontera. Marcar una sección entera como la isla para que funcione un botón hidrata cada párrafo estático que hay dentro, y el framework re-renderiza en el cliente un marcado que ya venía correcto en la respuesta.

**Directrices:**

1.  **Haz que la directiva corresponda a la posición y la prioridad del componente:**
    - `client:load` — por encima del pliegue e interactivo de inmediato: el buscador principal, un carrito en la cabecera, un control que es el tema de la página
    - `client:idle` — necesario pronto pero no primero: widgets secundarios, mejoras no críticas que pueden esperar a que el hilo principal se calme
    - `client:visible` — cualquier cosa por debajo del pliegue. Este es el valor por defecto correcto para la mayoría de las islas, y acepta un `rootMargin` para que la hidratación pueda empezar un poco antes de que el componente entre en el viewport
    - `client:media` — un componente que solo existe en ciertos breakpoints, típicamente un panel lateral solo para móvil o un panel solo para escritorio. Hidratar un menú móvil en escritorio es pagar por un componente que el usuario no puede alcanzar
    - `client:only` — sin renderizado en servidor en absoluto, para componentes que no pueden ejecutarse fuera del navegador. Exige nombrar el framework y cuesta un espacio en blanco hasta la hidratación, así que es un último recurso, no una forma de silenciar un error de desajuste
2.  **`client:load` es una afirmación que tiene que ser cierta:**
    - La afirmación es "el usuario puede interactuar con esto antes de hacer scroll". Si no puede, la directiva está mal
    - Un componente al que solo se llega tras hacer clic en otra cosa no está por encima del pliegue en ningún sentido significativo
    - Al auditar un sitio existente, la victoria más rápida suele ser releer cada `client:load` del código y hacerse esa única pregunta
3.  **Traza la isla alrededor de la interactividad, no alrededor de la sección:**
    - La isla es el control de filtrado, no la sección de resultados; los botones de las pestañas, no los paneles; el formulario, no la página que lo contiene
    - El contenido estático llega a una isla a través de slots, así que se renderiza una vez en tiempo de compilación y se pasa como _HTML_ en lugar de ser re-renderizado por el cliente
4.  **Las islas se hidratan de forma independiente, y esa es una propiedad estructural que conviene aprovechar:**
    - A diferencia de una aplicación de página única, una isla pesada al final de la página no bloquea una isla ligera arriba — cada una se solicita y se hidrata según su propio calendario
    - Así que la estructura correcta no es "menos islas", es "cada isla con su precio correcto". Varias islas pequeñas y bien dirigidas superan a una grande que hidrata todo de golpe
5.  **Aplaza el trabajo de servidor con islas de servidor en lugar de enviarlo al cliente:**
    - `server:defer` renderiza un componente bajo demanda después del esqueleto estático, manteniendo la página prerenderizada mientras un fragmento personalizado o lento llega por separado
    - Esta es la respuesta a "la página es estática salvo por esta franja dinámica" — necesita un adaptador, y no hidrata nada en el cliente
6.  **Una directiva es una señal de revisión cuando falta en el razonamiento del diff:**
    - El hallazgo no es "esto usa `client:load`"; es "esto usa `client:load` y está por debajo del pliegue"
    - Un componente sin ninguna directiva es _HTML_ estático — correcto y gratis cuando el componente no tiene comportamiento, y un error solo cuando se suponía que el componente era interactivo

**Incorrecto (todo hidratado de inmediato, y la isla trazada alrededor de contenido estático):**

```astro
---
// src/pages/pricing.astro
import PricingSection from '@components/PricingSection'; // React
import ComparisonChart from '@components/ComparisonChart'; // React, pesado
import MobileNav from '@components/MobileNav'; // React
---

<!-- Mal: la sección entera es una isla para que funcione un toggle que hay dentro.
     Cada titular, párrafo y precio se re-renderiza en el cliente -->
<PricingSection client:load plans={plans} />

<!-- Mal: por debajo del pliegue, y su bundle se solicita durante la carga inicial -->
<ComparisonChart client:load data={comparison} />

<!-- Mal: hidratado en todos los viewports, incluidos los que nunca lo muestran -->
<MobileNav client:load links={links} />
```

**Correcto (la frontera envuelve la parte interactiva, y cada directiva tiene su precio):**

```astro
---
// src/pages/pricing.astro
import PlanCard from '@components/PlanCard.astro'; // marcado estático, cero JS
import BillingToggle from '@components/BillingToggle'; // React: el único estado aquí
import ComparisonChart from '@components/ComparisonChart'; // React, pesado
import MobileNav from '@components/MobileNav'; // React
---

<section>
  <h2>Pricing</h2>

  <!-- La isla es el toggle, no la sección que lo rodea -->
  <BillingToggle client:load />

  <!-- Las tarjetas estáticas siguen siendo estáticas -->
  {plans.map((plan) => <PlanCard plan={plan} />)}
</section>

<!-- Por debajo del pliegue: su JavaScript no se solicita hasta que el lector llega -->
<ComparisonChart client:visible={{ rootMargin: '200px' }} data={comparison} />

<!-- Solo se hidrata en los viewports que de verdad pueden abrirlo -->
<MobileNav client:media="(max-width: 768px)" links={links} />
```

Referencia: [Template directives reference](https://docs.astro.build/en/reference/directives-reference/)
