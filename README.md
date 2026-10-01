# Pelagos — Underwater Archaeology Conservation Log

Este caso de estudio aplica una **lista doblemente enlazada** a la bitácora de conservación de un artefacto arqueológico recuperado de un naufragio. Cada nodo representa una observación, tratamiento o transferencia; sus enlaces `previous` y `next` permiten recorrer el historial hacia atrás y hacia adelante, insertar una anotación en la secuencia y eliminar o editar registros.

La historia de demostración es ficticia y está guardada en `data/timeline.json`. El backend está escrito en Python con clases y módulos separados; el frontend usa HTML, CSS y JavaScript. El almacenamiento local en JSON no requiere servicios externos ni paquetes adicionales.

## Ejecutar

Requiere Python 3.10 o posterior. Desde la carpeta del proyecto:

```powershell
python main.py
```

Abre <http://127.0.0.1:8000>. Detén el servidor con `Ctrl+C`. Los cambios se guardan en `data/timeline.json`.

## Estructura

```text
.
├── app/
│   ├── models/
│   │   ├── doubly_linked_list.py
│   │   └── treatment_event.py
│   ├── services/
│   │   └── timeline_service.py
│   ├── storage/
│   │   └── json_timeline_repository.py
│   └── server.py
├── data/
│   └── timeline.json
├── static/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── tests/
├── main.py
└── README.md
```

## API local

- `GET /api/events` — lista la bitácora desde la cabeza hasta la cola.
- `GET /api/events?direction=reverse` — la recorre desde la cola hasta la cabeza.
- `POST /api/events` — agrega una entrada en la posición indicada por `index`.
- `PUT /api/events/{id}` — actualiza una entrada sin cambiar su posición.
- `DELETE /api/events/{id}` — quita una entrada de la secuencia.

Los campos obligatorios de una entrada son `recorded_at`, `title`, `location`, `conservator` y `treatment`; `materials` y `notes` son opcionales.

## Pruebas

```powershell
python -m unittest discover -v
```
