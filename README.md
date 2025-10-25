**Ingeniería de Software (Unidad 1)**.

# API de Gestión de Pagos

Este proyecto implementa una API RESTful simple para la gestión de un sistema de pagos, desarrollada con **FastAPI**. La API permite crear, visualizar y modificar pagos, aplicando reglas de negocio específicas para la validación de transacciones. La persistencia de los datos se gestiona a través de un archivo local `data.json`.

## 📋 Funcionalidades y Endpoints

La API expone los siguientes endpoints para interactuar con el sistema de pagos:

| Método HTTP | Ruta                                     | Descripción                                                                 |
| :---------- | :--------------------------------------- | :-------------------------------------------------------------------------- |
| `GET`       | `/payments`                              | Devuelve una lista de todos los pagos registrados en el sistema.              |
| `POST`      | `/payments/{payment_id}`                 | Registra un nuevo pago en el sistema con estado `REGISTRADO`.                 |
| `POST`      | `/payments/{payment_id}/update`          | Actualiza el monto (`amount`) y el método (`payment_method`) de un pago existente. |
| `POST`      | `/payments/{payment_id}/pay`             | Intenta procesar un pago, aplicando las reglas de negocio. Cambia el estado a `PAGADO` o `FALLIDO`. |
| `POST`      | `/payments/{payment_id}/revert`          | Revierte el estado de un pago a `REGISTRADO`.                               |

-----

## ⚙️ Lógica de Negocio

El endpoint `/payments/{payment_id}/pay` implementa reglas de validación específicas antes de autorizar un pago:

#### Método de Pago: `Tarjeta de Crédito`

  * **Condición 1**: El monto del pago debe ser estrictamente **menor a $10,000**.
  * **Condición 2**: No puede existir más de un pago con este método en estado `REGISTRADO` en todo el sistema.

#### Método de Pago: `PayPal`

  * **Condición 1**: El monto del pago debe ser estrictamente **menor a $5,000**.

Si alguna de estas condiciones no se cumple durante el intento de pago, la transacción se marcará con estado `FALLIDO` y la API devolverá un error `HTTP 409 Conflict`.

-----

## 🛠️ Tecnologías Utilizadas

  * **FastAPI**: Framework web para la construcción de APIs.
  * **Pydantic**: Para la validación de datos en los requests.
  * **Uvicorn**: Servidor ASGI para ejecutar la aplicación.
  * **Pytest**: Framework para la ejecución de los tests unitarios.
  * **Pytest-asyncio**: Plugin para permitir que Pytest ejecute tests asíncronos.

-----

## 🚀 Instalación y Configuración

Sigue estos pasos para configurar el entorno de desarrollo local.

1.  **Clonar el repositorio:**

    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```

2.  **Crear y activar un entorno virtual:** (Recomendado)

    ```bash
    # Crear el entorno
    python -m venv venv

    # Activar en macOS/Linux
    source venv/bin/activate

    # Activar en Windows
    .\venv\Scripts\activate
    ```

3.  **Crear el archivo `requirements.txt`** con el siguiente contenido:

    ```
    fastapi
    "uvicorn[standard]"
    pytest
    pytest-asyncio
    ```

4.  **Instalar las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

-----

## ▶️ Ejecución de la Aplicación

Para iniciar el servidor de la API, ejecuta el siguiente comando desde la raíz del proyecto:

```bash
uvicorn main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`. Puedes acceder a la documentación interactiva de la API (Swagger UI) en `http://127.0.0.1:8000/docs`.

-----

## ✅ Ejecución de los Tests

El proyecto cuenta con una suite de tests unitarios para garantizar la calidad y el correcto funcionamiento de la lógica de negocio y los endpoints.

Para ejecutar todos los tests, utiliza `pytest` desde la raíz del proyecto:

```bash
pytest
```

El resultado mostrará todos los tests que pasaron y, en caso de haberlos, los que fallaron con un reporte detallado del error.

-----

## 📂 Estructura del Proyecto

```
.
├── main.py             # Lógica de la API y endpoints
├── test_main.py        # Tests unitarios
├── data.json           # Archivo de almacenamiento de datos
└── requirements.txt    # Dependencias del proyecto
```

-----