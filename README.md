# OpenTech2 Bridge v0.1

**Open-source, read-only vehicle diagnostics starter with a Tech 2-inspired interface.**

Independent community project; **not** GM, Bosch, Saab, or official Tech 2 software. This does **not** emulate GM Tech 2 PCMCIA cards or perform vehicle security unlocking.

## Features and limitations

| Feature | v0.1 |
| --- | --- |
| Local web interface on Windows / macOS / Linux | ✅ |
| Clearly labeled demo mode, no car required | ✅ |
| 44-brand vehicle catalog | ✅ Names/metadata only |
| 7 Tech 2 card family entries | ✅ Metadata only |
| Recognize user-owned card images by SHA-256 | ✅ No card copying, execution, or parsing |
| Generic OBD-II sensor values (Mode 01) | ✅ ELM327-compatible USB serial; vehicle untested |
| Generic powertrain DTC reading (Mode 03) | ✅ Preliminary |
| OEM modules, SAE J2534, Tech 2/CANdi, PCMCIA emulation | ❌ Not implemented |
| SPS, ECU writing, immobilizer/key functions, security access | ❌ Not implemented |

**Read-only prototype.** Do not use it to reprogram or configure an ECU. Real-car and adapter compatibility are not yet verified.

## Run on macOS / Linux

```bash
git clone https://github.com/artepe/tech2.git
cd tech2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[serial]'
opentech2 serve --demo
```

Open **http://127.0.0.1:8765**. Remove `--demo` for a compatible USB ELM327 adapter. In the UI, select the serial port (macOS: `ls /dev/cu.*`, Linux: `ls /dev/serial/by-id/`) and a supported baud rate. Vehicle and adapter compatibility are not yet tested.

Windows (PowerShell): `py -m venv .venv`, `.venv\Scripts\Activate.ps1`, `py -m pip install -e ".[serial]"`, `opentech2 serve --demo`.

## Test

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

## User-owned Tech 2 PCMCIA image registry

```bash
opentech2 cards add /path/to/my-card.bin --family saab --label "My Saab card"
opentech2 cards list
```

This **only** stores the filename, size, selected card family, and SHA-256 hash in `~/.opentech2/cards.json`; the image is not copied, decrypted, emulated, or executed. Original manufacturer firmware and card images are not distributed.

## Architecture

- `src/opentech2/server.py`: localhost-only API + web UI
- `src/opentech2/adapters.py`: offline demo and optional ELM327 serial adapter
- `src/opentech2/diagnostics.py`: generic OBD-II response decoding
- `src/opentech2/catalog.py`: brand and card metadata
- `src/opentech2/cards.py`: SHA-256 card registry
- `src/opentech2/security.py`: fail-closed boundary for protected OEM actions
- `tests/`: unit and local HTTP tests

### Roadmap

1. Validate generic OBD-II reads with real USB adapters and documented test vectors.
2. Add manufacturer-specific **read-only** ECU identification.
3. Develop optional SocketCAN ISO-TP / J2534 transports and bench simulations.
4. Describe legally documented Tech 2 workflows with open metadata, without shipping OEM code.
5. Integrate *authorized* OEM service systems only after explicit user permission, safety checks, and per-vehicle validation.

The project does not provide seed-key exploits, security bypasses, immobilizer key programming, or ECU flashing.

## Security

Local server binds to `127.0.0.1` and has no remote telemetry. Changes to local UI/connection state require a session token; no write commands to a vehicle are implemented. No credentials or manufacturer card files should be committed to Git.

## License

MIT for this project's original code only; vehicle manufacturers' software remains separately licensed.
