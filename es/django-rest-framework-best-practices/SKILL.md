---
name: django-rest-framework-best-practices
description: Guías de optimización para Django y Django REST Framework. Esta skill define los estándares arquitectónicos y de rendimiento del back-end, centrados en la eficiencia del ORM, las estrategias de serialización y la seguridad de la API
license: MIT
metadata:
  author: gianllopez
  version: 1.3.0
---

# Buenas prácticas de Django REST Framework

Guía completa para el desarrollo con _Django_ y _Django REST Framework_. Contiene reglas priorizadas según su impacto en el rendimiento de la base de datos, los tiempos de respuesta y la seguridad.

## Cuándo aplicarla

Consulta estas guías cuando:

- Diseñes o modifiques modelos de _Django_ y esquemas de base de datos (_PostgreSQL_)
- Implementes serializadores de _Django REST Framework_ y lógica de validación de datos
- Desarrolles vistas de _API_ usando _ViewSets_ o _Generic Views_ de _Django REST Framework_
- Optimices interacciones con la base de datos mediante el ORM de _Django_ (p. ej., `select_related`, `prefetch_related`)
- Gestiones flujos de autenticación, permisos personalizados y políticas de throttling
- Escribas comandos de gestión personalizados de _Django_ para tareas administrativas
- Implementes middleware para el procesamiento global de solicitudes o respuestas
- Manejes señales y receptores de _Django_ para lógica de eventos desacoplada
- Estructures aplicaciones nuevas y definas dependencias dentro del proyecto _Django_
- Personalices la interfaz de administración de _Django_ para la gestión interna de datos

## Categorías de reglas por prioridad

| Prioridad | Categoría                 | Impacto máximo | Prefijo |
| :-------- | :------------------------ | :------------- | :------ |
| 1         | Arquitectura y estructura | HIGH           | `arch-` |
| 2         | Configuración y DevOps    | HIGH           | `conf-` |
| 3         | ORM y base de datos       | HIGH           | `arch-` |
| 4         | API y serialización       | HIGH           | `arch-` |

La prioridad ordena dónde mirar primero; el impacto máximo es el de la regla más fuerte de la sección, y coincide con la tabla de contenidos de `AGENTS.md`. Discrepan a propósito — una sección puede contener una regla bloqueante y varias que solo llegan a producir sugerencias.

## Referencia rápida

### 1. Arquitectura y estructura (HIGH)

- `arch-app-structure` - Exige el directorio `apps/` y modelos/vistas basados en paquetes

### 2. Configuración y DevOps (HIGH)

- `conf-settings-structure` - Ajustes modulares (base/development/production) y secretos seguros
- `conf-deployment-topology` - Superposiciones de _Compose_ en capas, proxy inverso _Caddy_, imagen sin root con un entrypoint de release, _gunicorn_ y temporizadores de _systemd_
- `conf-env-dependencies` - `.venv` segregado y archivos de requisitos divididos

### 3. ORM y base de datos (HIGH)

- `arch-orm-model-structure` - Un modelo por archivo, opciones meta estrictas y tipado

### 4. API y serialización (HIGH)

- `arch-api-serializer-definition` - Nomenclatura basada en la acción, declaración explícita de campos ordenados según el modelo y uno por línea, y delegación de la representación extraída en el tercer serializador que la necesita
- `arch-view-definition` - Uso de vistas genéricas, tipado estricto de _APIView_ y declaración explícita de seguridad
- `arch-url-registration` - Imports de vistas a nivel de módulo, agrupación por dominio, orden create/list/detail y llamadas `path()` expandidas

## Cómo usarla

Lee los archivos de regla individuales para explicaciones detalladas y ejemplos de código:

```
./rules/*.md
```

Cada archivo de regla contiene:

- Una explicación breve de por qué importa
- Un ejemplo de código incorrecto con su explicación
- Un ejemplo de código correcto con su explicación
- Contexto adicional y referencias

## Documento compilado completo

Para la guía completa con todas las reglas expandidas: `AGENTS.md`
