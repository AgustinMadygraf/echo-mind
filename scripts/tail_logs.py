#!/usr/bin/env python3
"""Observabilidad: inspecciona los logs del servicio echo-mind en la VPS vía SSH.

Uso:
    python3 scripts/tail_logs.py [-n LINES] [-f] [--host HOST] [--port PORT]

Ejemplos:
    python3 scripts/tail_logs.py -n 30
    python3 scripts/tail_logs.py -f
    python3 scripts/tail_logs.py --host root@168.181.184.103 -n 50
"""

import argparse
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Observabilidad de logs del servicio echo-mind en la VPS."
    )
    parser.add_argument(
        "-n",
        "--lines",
        type=int,
        default=30,
        help="Número de líneas a consultar (por defecto: 30).",
    )
    parser.add_argument(
        "-f",
        "--follow",
        action="store_true",
        help="Seguir logs en tiempo real (journalctl -f).",
    )
    parser.add_argument(
        "--host",
        default="168.181.184.103",
        help="IP o target SSH (por defecto: 168.181.184.103).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5932,
        help="Puerto SSH (por defecto: 5932).",
    )
    return parser.parse_args()


def build_ssh_command(host: str, port: int, lines: int, follow: bool) -> list[str]:
    target = host if "@" in host else f"root@{host}"

    # El comando remoto se pasa como UN argumento: sshd ejecuta el login shell
    # del host remoto, que es quien parsea los espacios/opciones. No hacer
    # shlex.quote, o el shell remoto verá las comillas como parte del nombre.
    journal_cmd = "journalctl -u echo-mind"
    if follow:
        journal_cmd += " -f"
    else:
        journal_cmd += f" -n {lines} --no-pager"

    return ["ssh", "-T", "-p", str(port), target, journal_cmd]


def main() -> int:
    args = parse_args()
    cmd = build_ssh_command(args.host, args.port, args.lines, args.follow)

    print(f"==> Conectando a {args.host}:{args.port} "
          f"({'follow' if args.follow else f'{args.lines} líneas'})...")

    try:
        result = subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n==> Interrupción por teclado (Ctrl+C). Saliendo...", file=sys.stderr)
        return 130
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
