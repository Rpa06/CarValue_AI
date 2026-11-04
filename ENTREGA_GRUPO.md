# Entrega · CarValue AI

**Grupo:** ChupiFantasticos2

**Repositorio GitHub (privado, con acceso al profesor):** https://github.com/Rpa06/CarValue_AI

| Integrante | Parte implementada | Rama | 2 commits propios | URL del PR | ¿Quién revisó? |
|---|---|---|---|---|---|
| Rafael Pontes | 1,4,5 | Feat/flask, feat/docker feat/vision | Sí |https://github.com/Rpa06/CarValue_AI/pull/5|Cristofer|
| Cristofer | 2,3 | Feat/Jupyter+PostgreSQL, feat/ModeloPersistencia | Sí/No |https://github.com/Rpa06/CarValue_AI/pull/3|Rafael Pontes|
| ... (si hay 3) | ... | ... | Sí/No | ... | ... |

## Pruebas de funcionamiento

- [si] Docker Compose: 3 servicios activos.
- [si] `SELECT COUNT(*) FROM anuncios` devuelve 50000.
- [si] `GET /health` OK.
- [si] Formulario POST sin JavaScript; fotografía recibida en Flask.
- [si] Modo `MOCK` integra modelo ML + SQLAlchemy y guarda tasación.
- [si] `/historial` muestra tasación.
- [si] Modo real Cohere (`VISION_MOCK=0`): probado / no probado por falta de clave o límite de uso (explicar).
- [si] `docker compose exec app pytest -q`: ___ tests superados.
- [si] `.env` no está versionado.
- [si] Prompt propio escrito en `app/vision.py` (sin usar uno prefabricado).
- [si] Formulario HTML y página de resultado programados por el equipo.

## Reflexión breve (4 preguntas)

**1. HTTP frente a SQL:** ...
HTTP permite conectar el navegador a a la aplicacion flask y recibir respuestas. SQL permite consultar y guardar datos.

**2. Host `db` frente a `localhost`:**
db es el nombre del servicio, localhost apunta al contenedor de la aplicacion no a la base de datos.

**3. Valor del PR respecto a commits directos en `main`:** ...
Permite analizar la colaboracion de compañeros y evita dejar fragil el main, al proteger la rama de problemas o commit erroneos y permite mejorar el flujo de trabajo entre seniors y junior al ayudar a revisar y aprobar trabajo.

**4. Qué hacemos si Cohere devuelve `unknown`:** ...
No asignamos valor por defecto. Mostramos un mensaje de error y pedimos otra foto.

## Incidencias que no pudimos resolver (si las hay)

Tuvimos incidencios con versionado de github (Cristofer Carceller) que sabemossolucionar pero por falta de tiempo no lo hicimos.

## BONUS (solo si se ha hecho)

- [ ] `/estadisticas` muestra gráfica(s) basadas en consultas a PostgreSQL `anuncios`.
- [ ] `/estadisticas/grafico.png` responde `image/png`.
- [ ] PR `feature/dashboard` revisado: URL ___

## Decisiones de implementación

**Criterio del prompt (cómo definimos las categorías y el caso `unknown`):** ...
Lenguaje simple y puntual y unkown nos basamos en el hehco de no poder apreciar la totalidad.


**Decisión del HTML (atributos de formulario y envío de foto):** ...
No hubo decision fue asistido por IA.

**USO DE IA**
Se uso en IA para buscar rapidamente como es la API de cohere, desarrollo de codigo largo y tedioso.
Desarrollo de HTML