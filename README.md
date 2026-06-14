# Mundial 2026 Tracker — V1.2.2

App web estática para seguir el Mundial 2026: partidos diarios en horario español, clasificaciones, resultados, goleadores y cruces.





## Cambios V1.2.2

- Corregida la cobertura de TV en España.
- Añadidos los 17 partidos de fase de grupos emitidos en abierto por RTVE/La 1.
- Alemania - Curazao ya aparece como `La 1 · RTVE Play · DAZN`.
- DAZN sigue como canal por defecto para el resto.
- En eliminatorias se mantiene `DAZN · RTVE por confirmar` hasta que se actualice `tv-spain.json`.

## Cambios V1.2.1

- España queda destacada visualmente cuando aparece en partidos, grupos, resultados, goleadores o cruces.
- El resaltado usa una burbuja discreta en amarillo/rojo, con algo más de peso visual sin romper la estética.

## Cambios V1.2

- Añadida televisión en España en cada partido.
- Nuevo archivo externo `tv-spain.json` para actualizar canales sin tocar el código.
- Filtro de TV: todos, solo abierto, RTVE, DAZN y por confirmar.
- Reglas automáticas para eliminatorias: España, final y partidos pendientes de confirmación.
- Fallback prudente: donde no haya dato concreto, se muestra DAZN o “RTVE por confirmar”.

## Cómo actualizar la TV

Edita `tv-spain.json` en GitHub. No hace falta modificar `index.html`, `styles.css` ni `app.js`.

Ejemplo:

```json
"66456994": {
  "channels": ["La 1", "RTVE Play", "DAZN"],
  "free_to_air": true,
  "status": "confirmed",
  "label": "La 1 · RTVE Play · DAZN"
}
```

Estados recomendados:

- `confirmed`: confirmado.
- `probable`: probable / regla de fallback.
- `tbc`: por confirmar.

## Cambios V1.1.2

- Selector de fecha más compacto en móvil.
- Eliminado el texto explicativo redundante bajo las pestañas.
- Pestañas más compactas.
- Estado de partido pendiente mostrado como “Próximo”.
- Ajustes finos de altura para que los partidos queden más arriba.

## Cambios V1.1.1

- Banderas junto a las selecciones en partidos, grupos, resultados, goleadores y cruces.
- Icono visual de copa en la cabecera y favicon de la app.

## Cambios V1.1

- Interfaz mobile-first.
- Los partidos del día aparecen arriba, sin hacer scroll en móvil.
- Look & feel más deportivo, claro y visual.
- Selector de fecha compacto.
- Fuente de datos, buscador y leyenda movidos a bloques plegables.
- Resumen del día con partidos finalizados y pendientes.

## Archivos

- `index.html`
- `styles.css`
- `app.js`
- `README.md`

## Uso local

Abre `index.html` directamente o sirve la carpeta con:

```bash
python -m http.server 8000
```

Después abre:

```text
http://localhost:8000
```

## Publicación en GitHub Pages

Sube los cuatro archivos a la raíz del repositorio y espera a que GitHub Pages publique la nueva versión.

## Nota de datos

La fuente gratuita por defecto es OpenFootball. No garantiza actualización live minuto a minuto.
