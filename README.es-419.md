# Skill de subtítulos de video de AKB48 para Codex

[English](README.md) · [Русский](README.ru.md) · [한국어](README.ko.md) · [Español (LatAm)](README.es-419.md) · [Bahasa Indonesia](README.id.md) · [ไทย](README.th.md) · [简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md)

**Esta versión en español es un borrador; se recomienda revisión de una persona nativa antes de considerarla definitiva.**


Flujo reutilizable para traducir y subtitular videos de AKB48 y 48 Group. Guía a Codex para separar diálogos, atribución de voces, canciones y textos en pantalla; comprobar los nombres; y revisar los subtítulos y el video renderizado.

El repositorio incluye un skill de Codex, perfiles de idioma iniciales, un verificador básico de SRT, instrucciones de instalación y dos ejemplos visuales de episodios recientes traducidos al ruso. El perfil ruso se basa en un flujo aplicado a episodios completos. El perfil coreano es un borrador que necesita revisión de una persona nativa; los demás perfiles son puntos de partida para colaboradores.

## Vista previa

**Episodio 12 — identificación de quien habla y panel compacto** ([video original](https://www.youtube.com/watch?v=aPznmLtjedw))

![Ejemplo de subtítulos del episodio 12](examples/preview-episode-12.jpg)

*Fotograma citado: AKB48, **AKB48の全力エンタメ学園**, episodio 12 (18 de abril de 2026), [video original en YouTube](https://www.youtube.com/watch?v=aPznmLtjedw).* Se incluye para analizar técnicamente la etiqueta de identificación de quien habla y el panel compacto de subtítulos traducidos. Permite evaluar la separación entre el nombre y el diálogo sin depender únicamente del color.

**Episodio 13 — panel compacto durante la escena final de apretones de manos** ([video original](https://www.youtube.com/watch?v=mHF3TEk6lwQ))

![Ejemplo de subtítulos del episodio 13](examples/preview-episode-13.jpg)

*Fotograma citado: AKB48, **AKB48の全力エンタメ学園**, episodio 13 (25 de abril de 2026), [video original en YouTube](https://www.youtube.com/watch?v=mHF3TEk6lwQ).* Se utiliza para explicar la colocación de los subtítulos durante la escena de apretones de manos. El análisis se centra en la legibilidad y la relación con los elementos visuales originales, no en reproducir el episodio como entretenimiento.

Ambas imágenes son **fragmentos atribuidos para comentar aspectos técnicos del diseño de subtítulos**; no son recursos de libre reutilización ni sustituyen los episodios originales. Los derechos sobre las imágenes, los intérpretes, los logotipos y demás elementos de terceros pertenecen a sus respectivos titulares. La licencia **MIT no cubre estas capturas**. Indicar la fuente no concede por sí mismo permiso para redistribuirlas. Consulta [NOTICE](NOTICE) para las fuentes y las consideraciones sobre la cita en Japón. No se incluyen los videos ni los subtítulos completos.

## Usar con Codex

Clona el repositorio y abre su carpeta en Codex. El skill está en `.agents/skills/akb48-video-subtitles/` y Codex puede detectarlo como skill del proyecto. Para usarlo en otros proyectos, copia esa carpeta al directorio de skills de Codex: normalmente `%USERPROFILE%\.codex\skills\akb48-video-subtitles` en Windows o `$CODEX_HOME/skills/akb48-video-subtitles` si `CODEX_HOME` está configurado. Inicia una sesión nueva de Codex después de instalarlo.

Invócalo con `$akb48-video-subtitles` o pide traducir/revisar un video de AKB48 e indica el idioma de destino y los archivos que necesitas. Proporciona un video local o una fuente autorizada, el reparto y la lista de nombres si los tienes, y los formatos deseados. El flujo descrito no requiere una clave de API.

## Configuración rápida

Se requiere Python 3.11 o posterior, FFmpeg y FFprobe. Para renderizar ASS, FFmpeg debe incluir libass. Instala FFmpeg con el gestor de paquetes de tu sistema y asegúrate de que `ffmpeg` y `ffprobe` estén en `PATH`.

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
