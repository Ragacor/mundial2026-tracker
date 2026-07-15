# Mundial 2026 Tracker — V1.3.10

App web estática para seguir el Mundial 2026: partidos diarios en horario español, clasificaciones, resultados, goleadores y cruces.

















## Cambios V1.3.10

- Calendario actualizado a 15 de julio de 2026:
  - Francia 0-2 España.
  - España clasificada para la final.
  - Inglaterra - Argentina: miércoles 15 de julio a las 21:00 (hora peninsular).
  - Final: España vs ganador de Inglaterra - Argentina, domingo 19 de julio a las 21:00.
- Televisión actualizada:
  - Inglaterra - Argentina → `La 1 · RTVE Play · DAZN`.
  - Final → `La 1 · RTVE Play · DAZN`.
- Resumen añadido:
  - Francia - España → enlace directo a RTVE con resumen en vídeo y resultado.

## Cambios V1.3.9

- Calendario actualizado a 11 de julio de 2026:
  - Francia 2-0 Marruecos.
  - España 2-1 Bélgica.
  - Semifinal definida: Francia - España, martes 14 de julio a las 21:00 (hora peninsular).
  - Noruega - Inglaterra: sábado 11 de julio a las 23:00.
  - Argentina - Suiza: madrugada del 11 al 12 de julio a las 03:00.
- Televisión actualizada:
  - Francia - España → `La 1 · RTVE Play · DAZN`.
  - Final → `La 1 · RTVE Play · DAZN`.
  - Segunda semifinal → `DAZN · RTVE por confirmar` hasta confirmación específica.
- Nuevos resúmenes directos RTVE:
  - Francia - Marruecos.
  - España - Bélgica.
- Nuevo archivo `schedule-overrides.json` para garantizar cruces y resultados recientes aunque OpenFootball tarde en actualizar.
- Nuevo archivo `videos-rtve-manual.json` para conservar enlaces directos verificados sin que el workflow automático los sobrescriba.

## Cambios V1.3.8

- Actualizada la televisión de los cuartos de final con información vigente a 9 de julio de 2026.
- Francia - Marruecos → `La 1 · RTVE Play · DAZN`
- España - Bélgica → `La 1 · RTVE Play · DAZN`
- Noruega - Inglaterra → `DAZN`
- Argentina - Suiza → `DAZN`
- La app ahora admite `explicit_fixtures` para marcar partidos de eliminatorias como DAZN solamente cuando RTVE no los anuncia en abierto.

## Cambios V1.3.7

- Restaurados los resúmenes directos que se habían perdido al sobrescribir `videos-rtve.json`.
- Eliminada definitivamente la búsqueda genérica de RTVE.
- Añadidos enlaces directos/manuales para partidos de eliminatorias ya jugados:
  - Países Bajos - Marruecos
  - Costa de Marfil - Noruega
  - Francia - Suecia
  - Estados Unidos - Bosnia Herzegovina
  - España - Austria
  - Argentina - Cabo Verde
  - Australia - Egipto
  - Colombia - Ghana
- La app solo muestra `Resumen RTVE` cuando hay enlace directo útil.

## Cambios V1.3.6

- Eliminado el botón genérico `Buscar resumen RTVE`.
- La app vuelve a mostrar únicamente enlaces directos y útiles: `Resumen RTVE`.
- Si no hay enlace exacto en `videos-rtve.json`, no se muestra ningún botón.
- Mantiene el workflow automático V1.3.5 para intentar encontrar resúmenes, pero evita enviar al usuario a búsquedas genéricas de baja calidad.

## Cambios V1.3.5

- Automatización de resúmenes RTVE más fuerte.
- El script ya no depende solo de la colección de resúmenes.
- Ahora carga partidos finalizados desde OpenFootball y busca en RTVE partido a partido.
- Para cada partido sin vídeo intenta búsquedas como:
  - `Francia Suecia resumen Mundial 2026`
  - `Switzerland Algeria resumen Mundial 2026`
  - `Australia Egypt goles Mundial 2026 RTVE`
- Mantiene los vídeos ya existentes y añade nuevos si encuentra enlaces relevantes.
- Coste económico: 0 €, usando GitHub Actions en repositorio público.

## Cambios V1.3.4

- Añadido botón de fallback `Buscar resumen RTVE` en partidos finalizados sin enlace exacto.
- Si `videos-rtve.json` contiene el resumen, se muestra `Resumen RTVE`.
- Si no contiene el resumen, se muestra `Buscar resumen RTVE` y abre la búsqueda de RTVE con los equipos del partido.
- Esto evita que partidos finalizados se queden sin ninguna vía para localizar el resumen.

## Cambios V1.3.3

- Mejorado el script automático de resúmenes RTVE.
- Ya no busca solo una URL concreta tipo `resumen-partido-mundial-2026`.
- Ahora escanea enlaces RTVE Play más ampliamente e identifica selecciones por alias inglés/español.
- Añade logs con los partidos detectados para depurar desde GitHub Actions.
- Mantiene vídeos ya existentes y solo añade nuevos cuando los encuentra.

## Cambios V1.3.2

- Mejorado el cruce entre nombres en inglés de OpenFootball y nombres en español de RTVE.
- Añadidos alias para casos como:
  - Switzerland / Suiza
  - Algeria / Argelia
  - Egypt / Egipto
  - Germany / Alemania
  - Curacao / Curazao
- Esto mejora la aparición del botón `Resumen RTVE` cuando RTVE publica el resumen con nombres en español.
- La televisión en directo sigue dependiendo de `tv-spain.json`: solo se marca RTVE/La 1 cuando el partido esté confirmado.

## Cambios V1.3.1

- Actualizada televisión de eliminatorias.
- Paraguay - Francia marcado como `La 1 · RTVE Play · DAZN`.
- Añadidos también Brasil - Noruega y Portugal - España como partidos RTVE/La 1.
- Se mantiene `DAZN · RTVE por confirmar` para eliminatorias sin confirmación específica.

## Cambios V1.3

- Añadido botón `▶ Resumen RTVE` en partidos finalizados cuando exista enlace.
- Nuevo archivo `videos-rtve.json`.
- Nueva automatización con GitHub Actions: `.github/workflows/update-rtve-videos.yml` y `scripts/update_rtve_videos.py`.
- La automatización consulta la colección pública de resúmenes de RTVE y actualiza `videos-rtve.json`.
- No se incrustan vídeos: la app abre la página de RTVE Play en una pestaña nueva.
- La TV en España se cruza por pareja de selecciones para evitar errores por IDs externos.

## Cómo activar la automatización de RTVE

1. Sube todos los archivos y carpetas del ZIP al repositorio.
2. En GitHub entra en `Actions`.
3. Si GitHub te pide activar workflows, pulsa `I understand my workflows, go ahead and enable them`.
4. Abre el workflow `Update RTVE videos`.
5. Pulsa `Run workflow` para probarlo manualmente.
6. Después se ejecutará solo varias veces al día.

## Archivos nuevos

- `videos-rtve.json`
- `scripts/update_rtve_videos.py`
- `.github/workflows/update-rtve-videos.yml`

## Cambios V1.2.3

- Corrección crítica del módulo de TV en España.
- La app ya no depende solo de IDs externos para asignar TV.
- Ahora cruza también por fecha en España + selecciones.
- Alemania - Curazao aparece correctamente como `La 1 · RTVE Play · DAZN`.
- Evita que partidos confirmados en RTVE aparezcan erróneamente solo como DAZN.

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
