---
title: Definición, nomenclatura y delegación de serializadores
impact: HIGH
description: Exige imports condicionales, convenciones de nombres basadas en la acción, declaración explícita de campos uno por línea expandida, y delegación de la respuesta extraída a DelegateRepresentationMixin en cuanto tres serializadores de escritura la necesitan.
tags: django-rest-framework, serializers
---

## Definición, nomenclatura y delegación de serializadores

**Impacto (HIGH):** Separar los serializadores por acción (lectura frente a escritura) evita abstracciones que se filtran. La delegación de la respuesta solo merece abstraerse cuando la repetición lo demuestra: un único serializador de escritura que reconfigura su respuesta se lee mejor con un `to_representation` local, mientras que una tercera copia de esa sobrescritura convierte al mecanismo, y no al mapeo, en lo que el proyecto mantiene.

**Directrices:**

1.  **Imports condicionales:**
    - **Simple:** si se hereda _solo_ de `ModelSerializer` sin campos personalizados, importa `ModelSerializer` directamente
    - **Complejo:** si se usan campos personalizados (p. ej., `CharField`), importa el módulo `serializers` y usa `serializers.ModelSerializer`
2.  **Convención de nombres:** usa sufijos específicos:
    - `*ListSerializer`: optimizado para colecciones
    - `*RetrieveSerializer`: lectura detallada de un solo objeto
    - `*CreateSerializer` / `*UpdateSerializer`: para operaciones de escritura
3.  **Delegación de la respuesta (operaciones de escritura):**
    - Un serializador de escritura (`Create`/`Update`) que deba devolver una representación distinta de su entrada (p. ej., la estructura completa de `UserRetrieveSerializer` tras crear un usuario) sobrescribe `to_representation` localmente mientras el proyecto tenga menos de tres serializadores así
    - Al llegar al tercero, extrae `DelegateRepresentationMixin` a `apps/common/mixins` y migra a él todos los serializadores que delegan — el conteo es a nivel de proyecto e independiente de a qué serializador apunte cada uno, porque el mixin factoriza el mecanismo y no el mapeo
    - Una vez que el mixin existe, es la única forma aceptada: una sobrescritura manual que quede atrás es exactamente la duplicación que la extracción eliminó
    - Declara el serializador de destino en `Meta.representation`
4.  **Declaración de campos:**
    - `Meta.fields` debe ser siempre una lista explícita `[...]`. Nunca uses `"__all__"` ni ninguna otra abreviatura
    - El orden de los campos en la lista debe coincidir con el orden en que están definidos en el modelo
    - Cada campo va en su propia línea, con una coma final después del último, por corta que sea la lista. La coma final es lo que fija esa disposición: cualquier formateador compatible con _Black_ mantiene expandido un literal expandido en cuanto está presente, de modo que un serializador de dos campos no vuelve a colapsarse en una línea mientras uno de cinco se queda expandido

**Incorrecto (campos implícitos, orden arbitrario o una lista colapsada):**

```python
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"  # Mal: expone campos no previstos; el orden no es determinista
```

```python
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        # Mal: el orden no coincide con la definición del modelo
        fields = [
            "name",
            "id",
            "phone",
        ]
```

```python
class InvoiceListSerializer(ModelSerializer):
    class Meta:
        model = Invoice
        # Mal: es lo bastante corta como para caber en una línea, así que se lee
        # distinto de cualquier serializador más largo, y el siguiente campo que
        # se añada reescribirá esta línea
        fields = ["id", "number"]
```

**Correcto (lista explícita ordenada según la definición del modelo):**

```python
# Orden de definición del modelo: id, phone, name, role
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        # Coincide con el orden de campos del modelo
        fields = [
            "id",
            "phone",
            "name",
            "role",
        ]
```

**Incorrecto (abstracción sin repetición, o repetición sin abstracción):**

```python
# ./apps/users/serializers/user_create_serializer.py — el único serializador que delega

from apps.common.mixins import DelegateRepresentationMixin

# Mal: un mixin compartido en apps/common/ con un único punto de uso.
# La indirección cuesta más que las tres líneas que reemplaza
class UserCreateSerializer(DelegateRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "identification",
            "name",
            "phone",
        ]
        representation = UserRetrieveSerializer
```

```python
# ./apps/invoices/serializers/invoice_create_serializer.py — la tercera sobrescritura de su tipo

class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "number",
            "customer",
            "total",
        ]

    # Mal: UserCreateSerializer y PaymentCreateSerializer ya cargan estas mismas
    # líneas. El mecanismo de delegación es ahora lo que el proyecto mantiene
    def to_representation(self, instance):
        from .invoice_retrieve_serializer import InvoiceRetrieveSerializer

        return InvoiceRetrieveSerializer(instance, context=self.context).data
```

**Correcto (sobrescritura local por debajo del umbral, mixin extraído al alcanzarlo):**

```python
# ./apps/users/serializers/user_create_serializer.py — uno de los dos serializadores que delegan

from rest_framework import serializers

from apps.users.models import User

class UserCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = User
        fields = [
            "identification",
            "name",
            "phone",
            "code",
        ]

    # Local, evidente y barato de borrar en cuanto un mixin lo reemplace.
    # El import se difiere para romper la referencia circular entre serializadores
    def to_representation(self, instance):
        from .user_retrieve_serializer import UserRetrieveSerializer

        return UserRetrieveSerializer(instance, context=self.context).data
```

```python
# ./apps/invoices/serializers/invoice_create_serializer.py — el tercero: extraer y migrar

from rest_framework import serializers

from apps.common.mixins import DelegateRepresentationMixin
from apps.invoices.models import Invoice
from apps.invoices.serializers.invoice_retrieve_serializer import InvoiceRetrieveSerializer

# Hereda del Mixin + Serializer
class InvoiceCreateSerializer(DelegateRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "number",
            "customer",
            "total",
        ]
        # Transforma la respuesta usando el serializador Retrieve
        representation = InvoiceRetrieveSerializer
```

Referencia: [DRF Customizing Serialization](https://www.django-rest-framework.org/api-guide/serializers/#customizing-serialization)
