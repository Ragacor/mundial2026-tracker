# Mundial 2026 Tracker

Aplicación web estática para seguir el Mundial de Fútbol 2026.

## Qué hace

- Muestra los partidos de cada día en horario español (Europe/Madrid).
- Convierte automáticamente los horarios de Estados Unidos, Canadá y México a España.
- Calcula clasificaciones de grupos a partir de los resultados disponibles.
- Muestra una tabla provisional de mejores terceros.
- Agrupa resultados por día.
- Agrega goleadores a partir de los eventos de gol disponibles en el JSON.
- Muestra los cruces de eliminatorias: ronda de 32, octavos, cuartos, semifinales, tercer puesto y final.
- Permite buscar por equipo, sede, grupo o ronda.
- Permite cargar un JSON manual/local si quieres usar otra fuente.

## Fuente de datos por defecto

La app usa por defecto:

https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json

OpenFootball es abierto y no requiere clave API. No es un servicio live minuto a minuto. Si quieres resultados, eventos, tarjetas, alineaciones o goleadores en tiempo real, conviene conectar una API deportiva tipo API-FOOTBALL o Sportmonks.

## Cómo ejecutarla en PC

1. Descomprime el ZIP.
2. Abre `index.html` en Chrome, Edge o Firefox.
3. Si el navegador bloquea alguna carga remota, usa una de estas opciones:
   - Sube la carpeta a GitHub Pages.
   - O ejecuta un servidor local:

```bash
python -m http.server 8000
```

Después abre:

```text
http://localhost:8000
```

## Cómo subirla a GitHub Pages

1. Crea un repositorio nuevo en GitHub.
2. Sube estos archivos a la raíz del repositorio:
   - `index.html`
   - `styles.css`
   - `app.js`
   - `README.md`
3. En GitHub: `Settings` → `Pages`.
4. En `Build and deployment`, selecciona:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/root`
5. Guarda. GitHub te dará una URL pública.

## Formato JSON compatible

La app espera un objeto así:

```json
{
  "name": "World Cup 2026",
  "matches": [
    {
      "round": "Matchday 1",
      "date": "2026-06-11",
      "time": "13:00 UTC-6",
      "team1": "Mexico",
      "team2": "South Africa",
      "score": { "ft": [2, 0], "ht": [1, 0] },
      "goals1": [{ "name": "Julián Quiñones", "minute": "9" }],
      "goals2": [],
      "group": "Group A",
      "ground": "Mexico City"
    }
  ]
}
```

## Limitación importante

La clasificación usa criterios provisionales: puntos, diferencia de goles, goles a favor y orden alfabético. Para una app oficial habría que implementar todos los criterios FIFA de desempate, incluyendo enfrentamientos directos, fair play y sorteo cuando aplique.
