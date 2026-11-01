# Skill de subtítulos de video de AKB48 para Codex

[English](README.md) · [Русский](README.ru.md) · [한국어](README.ko.md) · [Español (LatAm)](README.es-419.md) · [Bahasa Indonesia](README.id.md) · [ไทย](README.th.md) · [简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md)

**Esta versión en español es un borrador; se recomienda revisión de una persona nativa antes de considerarla definitiva.**


Flujo reutilizable para traducir y subtitular videos de AKB48 y 48 Group. Guía a Codex para separar diálogos, atribución de voces, canciones y textos en pantalla; comprobar los nombres; y revisar los subtítulos y el video renderizado.

El repositorio incluye un skill de Codex, perfiles de idioma iniciales, un verificador básico de SRT, instrucciones de instalación y dos ejemplos visuales de episodios recientes traducidos al ruso. El perfil ruso se basa en un flujo aplicado a episodios completos. El perfil coreano es un borrador que necesita revisión de una persona nativa; los demás perfiles son puntos de partida para colaboradores.

## Instalación rápida

Necesitas Git, Python 3.11+, FFmpeg/FFprobe con libass y acceso a Codex. Los comandos clonan el repositorio y verifican las herramientas; no instalan los requisitos. Abre la carpeta clonada en Codex e inicia un chat nuevo.

```sh
git clone https://github.com/ivst/akb48-video-subtitle-codex-skill.git
cd akb48-video-subtitle-codex-skill
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py --require-ass
```

## Ejemplo de prompt

```text
Usa $akb48-video-subtitles para traducir [ruta local del video o URL autorizada] al español latinoamericano, incluidos los textos en pantalla.
Entrega SRT y ASS separados, un video con subtítulos incrustados y el informe de comprobaciones. Usa el diseño compacto actual junto al borde inferior. Separa las voces con nombres verificados o roles neutrales; no unas voces desconocidas.
Omite la música de fondo y las letras. Revisa los nombres, el sentido del diálogo, los textos en pantalla y los fotogramas finales; registra las dudas. No publiques nada.
```

## Vista previa

### Diseño actual del skill — estilo del episodio 12

Ejemplo generado con el renderizador incluido: panel claro semitransparente, nombre y marca de color separados, y diálogo oscuro en seminegrita. Es el diseño predeterminado; una simple caja de fondo detrás del texto no es equivalente.

![Una persona](examples/compact-single-preview.jpg)

[Intercambio entre dos personas](examples/compact-preview.jpg) · [Diálogo largo y texto en pantalla](examples/compact-long-preview.jpg) · [ASS](examples/compact.ass)

**Episodio 12 — identificación de quien habla y panel compacto** ([video original](https://www.youtube.com/watch?v=aPznmLtjedw))

![Ejemplo de subtítulos del episodio 12](examples/preview-episode-12.jpg)

*Fotograma citado: AKB48, **AKB48の全力エンタメ学園**, episodio 12 (18 de abril de 2026), [video original en YouTube](https://www.youtube.com/watch?v=aPznmLtjedw).* Se incluye para analizar técnicamente la etiqueta de identificación de quien habla y el panel compacto de subtítulos traducidos. Permite evaluar la separación entre el nombre y el diálogo sin depender únicamente del color.

**Episodio 13 — panel compacto durante la escena final de apretones de manos** ([video original](https://www.youtube.com/watch?v=mHF3TEk6lwQ))

![Ejemplo de subtítulos del episodio 13](examples/preview-episode-13.jpg)

*Fotograma citado: AKB48, **AKB48の全力エンタメ学園**, episodio 13 (25 de abril de 2026), [video original en YouTube](https://www.youtube.com/watch?v=mHF3TEk6lwQ).* Se utiliza para explicar la colocación de los subtítulos durante la escena de apretones de manos. El análisis se centra en la legibilidad y la relación con los elementos visuales originales, no en reproducir el episodio como entretenimiento.

Ambas imágenes son **fragmentos atribuidos para comentar aspectos técnicos del diseño de subtítulos**; no son recursos de libre reutilización ni sustituyen los episodios originales. Los derechos sobre las imágenes, los intérpretes, los logotipos y demás elementos de terceros pertenecen a sus respectivos titulares. La licencia **MIT no cubre estas capturas**. Indicar la fuente no concede por sí mismo permiso para redistribuirlas. Consulta [NOTICE](NOTICE) para las fuentes y las consideraciones sobre la cita en Japón. No se incluyen los videos ni los subtítulos completos.

## Instalar para otros proyectos

Para usarlo en otros proyectos, copia `.agents/skills/akb48-video-subtitles/` al directorio de skills de Codex: normalmente `%USERPROFILE%\.codex\skills\akb48-video-subtitles` en Windows o `$CODEX_HOME/skills/akb48-video-subtitles` si `CODEX_HOME` está configurado. Inicia una sesión nueva de Codex después de instalarlo.

## Comprobaciones adicionales

Comprueba un SRT ya creado sustituyendo la ruta de ejemplo.

```powershell
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py ruta\a\dialogue.srt
```

Los scripts incluidos usan la biblioteca estándar de Python; no hace falta instalar paquetes con pip. Consulta los [requisitos de recursos](.agents/skills/akb48-video-subtitles/references/resources.md).

## Flujo de trabajo

1. Verifica el texto japonés y registra por separado los letreros, títulos, reglas y resultados.
2. Traduce con el perfil elegido y un glosario del episodio revisado.
3. Atribuye cada intervención solo cuando haya evidencia; deja neutrales las reacciones dudosas.
4. Crea SRT, ASS con estilo y/o MP4 según lo solicitado.
5. Revisa fotogramas a lo largo del episodio y el render final. Cuando corresponda, comprueba decodificación, tiempos, paquete y conservación del audio.

Consulta la [guía del flujo](.agents/skills/akb48-video-subtitles/references/workflow.md) y los [perfiles de idioma](.agents/skills/akb48-video-subtitles/references/languages/README.md).

## Recursos

Para un episodio típico de 1080p y 20–40 minutos, 8 GB de RAM y un procesador reciente de 4 núcleos sirven como punto de partida; 16 GB y 6–8 núcleos resultan más cómodos para ASR local. Deja alrededor de 10 GB libres para el original, temporales, render y respaldo. La GPU es opcional. El material 4K o de alto bitrate puede requerir bastante más. Son estimaciones: el uso real depende del códec, el modelo ASR y el codificador.

## Derechos y privacidad

Procesa y publica solo materiales cuyo uso tengas autorizado. No incluyas transcripciones de episodios, subtítulos completos, credenciales, cookies ni glosarios privados en contribuciones públicas si no tienes permiso para redistribuirlos. Los fotogramas de ejemplo muestran el diseño; los derechos del programa siguen perteneciendo a sus titulares.

## Licencia

La documentación y los scripts originales usan la licencia MIT. Las imágenes de ejemplo y el material del programa que aparece en ellas quedan excluidos; consulta [NOTICE](NOTICE) y [LICENSE](LICENSE).

## Comprobación completa del video

El informe de video incluye la decodificación completa del original y del resultado, errores del decodificador y comparación del número real de fotogramas (`check_decode.py`). El hash de audio tiene un límite de tiempo para toda la decodificación y evita bloqueos de los canales del proceso. `run_checks.py --media-timeout 1800` fija los segundos máximos por archivo. Se presupone que no hay conversión intencional de la frecuencia de fotogramas.

## Opcional: transcripción japonesa y guía detallada

**faster-whisper** permite obtener un borrador japonés o contrastar subtítulos. La traducción y la atribución de voces son pasos separados. Se instala en un entorno independiente; el modo CPU no requiere WSL ni GPU. Consulta la [instalación y el ejemplo de transcripción en inglés](.agents/skills/akb48-video-subtitles/references/transcription.md) y la [guía detallada en inglés](docs/workflow.en.md).

## Subtítulos por hablante y diseño compacto (0.5.0)

ASS/video requiere `work/presentation.json` revisado. `build_presentation.py` muestra nombres/roles y no une automáticamente voces desconocidas. El margen inferior es de 30px en el lienzo 1080p (20px a 720p). Las letras se omiten salvo petición explícita. Consulta el [esquema y los comandos](.agents/skills/akb48-video-subtitles/references/presentation.md) y la [nueva vista sintética](examples/compact-preview.jpg).
