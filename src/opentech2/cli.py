from __future__ import annotations
import argparse
import json
from .catalog import CARD_FAMILIES
from .cards import CardRegistry
from .server import make_server

def main(argv=None):
    parser = argparse.ArgumentParser(prog="opentech2",description="OpenTech2 Bridge - open, read-only diagnostics")
    sub=parser.add_subparsers(dest="command",required=True)
    web=sub.add_parser("serve",help="Käynnistä paikallinen selainkäyttöliittymä")
    web.add_argument("--port",type=int,default=8765)
    web.add_argument("--demo",action="store_true",help="Näytä selvästi merkitty testidata")
    cards=sub.add_parser("cards",help="Korttien metatietorekisteri (ei alkuperäisiä ohjelmistoja)")
    cards_sub=cards.add_subparsers(dest="cards_command",required=True)
    reg=cards_sub.add_parser("add",help="Laske omistamasi tiedoston SHA-256")
    reg.add_argument("file")
    reg.add_argument("--family",required=True,choices=[c.id for c in CARD_FAMILIES])
    reg.add_argument("--label",required=True)
    cards_sub.add_parser("list")
    sub.add_parser("doctor",help="Tarkista ohjelmiston perustiedot")
    args=parser.parse_args(argv)
    if args.command=="doctor":
        try: import serial; ser="asennettu"
        except ImportError: ser="puuttuu: pip install -e '.[serial]'"
        print("OpenTech2 v0.1 | OBD-II: vain luku | OEM / security: ei toteutettu | pyserial:",ser)
    elif args.command=="cards":
        registry=CardRegistry()
        value=registry.add(args.file,args.family,args.label) if args.cards_command=="add" else registry.list()
        print(json.dumps(value,ensure_ascii=False,indent=2))
    else:
        server=make_server(port=args.port,demo=args.demo)
        print(f"OpenTech2 Bridge: http://127.0.0.1:{server.server_port}")
        print("Tila:","DEMO" if args.demo else "ei yhteyttä; liitä ELM327 käyttöliittymästä")
        print("Vain paikallinen yhteys. Lopeta Ctrl+C")
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally: server.server_close()

if __name__ == "__main__": main()
