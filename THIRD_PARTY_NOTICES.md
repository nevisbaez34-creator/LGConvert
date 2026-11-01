# Componentes de terceros

LGConvert usa los siguientes programas externos. Sus licencias pertenecen a sus autores.

## yt-dlp

- Uso: descarga de video y audio.
- Licencia: The Unlicense.
- Código fuente: https://github.com/yt-dlp/yt-dlp

## FFmpeg

- Uso: conversión y procesamiento de audio y video (`ffmpeg.exe` y `ffprobe.exe`).
- Build utilizado: `2026-10-25-git-46f23be8b1-full_build` (gyan.dev).
- Licencia: GPLv3 (el build se compiló con `--enable-gpl` y `--enable-version3`).
- Código fuente correspondiente: commit `46f23be8b1` del repositorio oficial, https://git.ffmpeg.org/ffmpeg.git
- Aviso de copyright: Copyright (c) 2000-2026 the FFmpeg developers.

El build incluye librerías con licencias propias, como x264 y x265 (GPL), y otras bajo LGPL, MIT o BSD. Consulta el aviso de licencia que viene dentro del zip de gyan.dev.

## Nota

Esta información corresponde al build indicado. Si cambias a otra versión o al build "essentials" de una release, actualiza esta sección con la salida de `ffmpeg -version` del ejecutable que vayas a distribuir.
