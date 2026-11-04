"""Cohere Vision: una foto -> estado exterior + justificación breve."""
import base64
import json
import os
import re
from .config import ESTADOS

MODELO_VISION = "command-a-vision-07-2025"
PROMPT = """Analiza la fotografía adjunta para evaluar únicamente el aspecto exterior
visible del vehículo. Elige una sola categoría de esta lista cerrada:
- "like new": aspecto como nuevo, sin desgaste visible apreciable.
- "excellent": aspecto excelente, con desgaste mínimo.
- "good": buen estado general, con marcas pequeñas de uso.
- "fair": estado aceptable, con daños o desgaste visibles.

Si no se aprecia claramente un coche o la imagen no aporta evidencias suficientes
para evaluarlo (por ejemplo, muestra solo un detalle aislado), usa "unknown"; no
adivines ni completes información que no se vea. No infieras el estado del motor,
el historial de accidentes, el kilometraje real, averías ni el funcionamiento
mecánico a partir de la imagen.

Responde solo con un objeto JSON válido, sin introducción ni bloques Markdown,
con exactamente estas claves: "condition" y "reason". "condition" debe ser una
única etiqueta exacta de las cinco admitidas: "like new", "excellent", "good",
"fair" o "unknown". "reason" debe ser una explicación breve en español basada
solo en detalles visibles. No añadas otros campos ni puntuaciones de confianza."""


class VisionError(Exception):
    """Error de proveedor o de respuesta no interpretable."""


def parsear_respuesta(texto: str) -> tuple[str, str]:
    """Helper ya implementado: valida el JSON que responde la IA."""
    limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.I)
    if not limpio.startswith("{"):
        a, b = limpio.find("{"), limpio.rfind("}")
        if a >= 0 and b > a:
            limpio = limpio[a:b+1]
    try:
        obj = json.loads(limpio)
    except (ValueError, TypeError) as exc:
        raise VisionError("Cohere no devolvió un JSON interpretable.") from exc
    if not isinstance(obj, dict) or set(obj) != {"condition", "reason"}:
        raise VisionError("La respuesta de Cohere no contiene las claves JSON esperadas.")
    if not isinstance(obj["condition"], str) or not isinstance(obj["reason"], str):
        raise VisionError("Las claves condition y reason deben contener texto.")
    estado = obj["condition"].strip().lower()
    razon = obj["reason"].strip()[:350]
    if estado not in (*ESTADOS, "unknown"):
        raise VisionError(f"Cohere devolvió una categoría inesperada: {estado!r}")
    if not razon:
        raise VisionError("Cohere no proporcionó una justificación.")
    return estado, razon


def clasificar_estado(contenido: bytes, mimetype: str) -> tuple[str, str, str]:
    """Clasifica el aspecto exterior y devuelve (estado, razon, fuente)."""
    if os.getenv("VISION_MOCK", "0") == "1":
        return "good", "Modo demostración: estado fijo, sin analizar la fotografía.", "MOCK"
    token = os.getenv("COHERE_API_KEY", "").strip()
    if not token:
        raise VisionError("Falta COHERE_API_KEY en el archivo .env")
    if not PROMPT.strip():
        raise VisionError("Falta redactar el prompt visual: tarea C1-A.")
    if mimetype not in {"image/jpeg", "image/png", "image/webp"}:
        raise VisionError("El formato de imagen no es compatible con Cohere Vision.")

    try:
        import cohere
        import httpx
    except ImportError as exc:
        raise VisionError("No está instalado el cliente Python de Cohere.") from exc

    imagen_url = (
        f"data:{mimetype};base64,"
        f"{base64.b64encode(contenido).decode('ascii')}"
    )
    try:
        cliente = cohere.ClientV2(api_key=token)
        respuesta = cliente.chat(
            model=MODELO_VISION,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": imagen_url},
                        },
                    ],
                }
            ],
        )
    except (cohere.core.ApiError, httpx.RequestError) as exc:
        estado_error = getattr(exc, "status_code", None)
        detalle = f"HTTP {estado_error}" if estado_error else type(exc).__name__
        raise VisionError(
            f"No se pudo completar la clasificación con Cohere ({detalle}). "
            "Comprueba la conexión y COHERE_API_KEY."
        ) from exc

    try:
        bloques = respuesta.message.content
    except AttributeError as exc:
        raise VisionError("Cohere devolvió una respuesta sin contenido.") from exc
    if not isinstance(bloques, (list, tuple)):
        raise VisionError("Cohere devolvió un formato de contenido no válido.")

    textos = []
    for bloque in bloques:
        texto = (
            bloque.get("text")
            if isinstance(bloque, dict)
            else getattr(bloque, "text", None)
        )
        if isinstance(texto, str) and texto.strip():
            textos.append(texto)
    if not textos:
        raise VisionError("Cohere no devolvió texto para clasificar la fotografía.")

    estado, razon = parsear_respuesta("\n".join(textos))
    return estado, razon, "COHERE"
