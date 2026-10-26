# Reportes de prueba en hardware

[English](TESTING.md) · **Español**

Este proyecto publica 95 imágenes para 26 teclados, pero solo **una unidad**
(K13 Pro ISO RGB) se ha probado en hardware real. Los reportes de la comunidad
son la única forma de saber qué modelos funcionan de verdad, así que reportar es
un flujo de un clic.

## Reporta en 30 segundos

1. Pulsa **[Reportar una prueba](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml)**
   (también está enlazado en el README y en la carpeta de cada modelo).
2. Elige tu modelo, pega el nombre del fichero flasheado y su SHA-256, selecciona
   el resultado y pulsa **Submit**.
3. Ya está. El issue es público; puedes añadir detalles después.

Obtén el SHA-256 del fichero que flasheaste:

```bash
sha256sum firmware/<modelo>/<variante>/<fichero>.bin
# o en Windows (PowerShell):
Get-FileHash .\<fichero>.bin -Algorithm SHA256
```

**No** pegues direcciones MAC, números de serie, nombres de equipo ni rutas
personales.

## Qué pasa tras enviarlo

```
Formulario  ──►  etiqueta hardware-test
                      │
                      ├─ Resultado = Works     ──►  etiqueta tested-ok
                      └─ Resultado = Problems  ──►  etiqueta tested-problem
                                                      │
                              TESTED.md + tested.json se reconstruyen solos
                                (se publican en la rama tested-index)
```

- Reportar **no** es votar: un reporte cuenta solo si incluye modelo, variante y
  SHA-256 del binario.
- `tested-ok` significa "este binario exacto arrancó y fue usable al menos en una
  sesión corta". No significa que el modelo esté totalmente validado.
- Un maintainer puede pedir detalles o re-etiquetar el issue si el SHA no coincide
  con ninguna build publicada.
- El badge y los contadores del README se generan desde `docs/tested.json` en la
  [rama `tested-index`](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md),
  que el workflow [`tested-index`](../.github/workflows/tested-index.yml)
  reconstruye a partir de los issues etiquetados más la prueba del maintainer
  ([`docs/tested-seed.json`](tested-seed.json)). `main` sigue protegida: los
  ficheros generados se publican en su propia rama, nunca con push directo.

## Etiquetas

| Etiqueta | Significado |
|---|---|
| `hardware-test` | Cualquier issue creado desde el formulario |
| `tested-ok` | Binario flasheado y teclado usable |
| `tested-problem` | Binario flasheado pero algo va mal |
| `bug` | Defecto de firmware/herramientas confirmado por un maintainer |

También puedes ver la lista cruda:
[issues con `tested-ok`](https://github.com/thementalcoding/keychron-pro-firmware/issues?q=label%3Atested-ok).

## Buenos reportes

Un reporte útil incluye:

- modelo, variante y PID exactos (`lsusb | grep 3434`),
- **nombre del fichero** y **SHA-256** del firmware (identifica la build),
- SO anfitrión y adaptador Bluetooth (Linux: `lsusb`/`lspci`; macOS: Acerca de
  este Mac; Windows: Administrador de dispositivos),
- si se probó por USB, por Bluetooth o ambos,
- qué hiciste (escritura normal, editar keymap en VIA, suspensión/despertar,
  reconexión, RGB),
- si algo va mal: qué pasó, con qué frecuencia y si también ocurre con el firmware
  de fábrica.

## Para maintainers

Todo está automatizado; la única acción manual es revisar un reporte si su SHA no
coincide con una build publicada.

```bash
# Reconstruir el índice en local (necesita gh autenticado con lectura)
GITHUB_REPOSITORY=thementalcoding/keychron-pro-firmware \
  python3 tools/hardware_tests.py index

# Re-evaluar etiquetas de un issue
GITHUB_REPOSITORY=thementalcoding/keychron-pro-firmware \
  python3 tools/hardware_tests.py label 123
```

El workflow del índice publica los ficheros regenerados en la rama
`tested-index` (force-push del bot) porque `main` está protegida. El badge y el
enlace del README apuntan allí.
