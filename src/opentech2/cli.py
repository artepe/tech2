from __future__ import annotations
import argparse
import json
from .catalog import CARD_FAMILIES
from .cards import CardRegistry
from .inventory import analyze_inventory
from .chrysler300 import catalog as chrysler300_catalog
from .uds import SocketCanDidReader, parse_dids, read_demo_identification, UdsError
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
    inv=sub.add_parser("inventory",help="Tutki moduuli-/avainmetatietoja OFFLINE, ei ajoneuvokomentoja")
    inv.add_argument("file")
    uds=sub.add_parser("ecu-read",help="UDS 0x22 ECU-tunnisteiden vain-luku (SocketCAN Linux / demo)")
    uds.add_argument("--demo",action="store_true")
    uds.add_argument("--interface",help="Esim. can0 / vcan0 (Linux)")
    uds.add_argument("--tx-id",help="ECU:n fyysinen pyyntö-ID, esim. 0x7E0")
    uds.add_argument("--rx-id",help="ECU:n vastaus-ID, esim. 0x7E8")
    uds.add_argument("--dids",default="F190,F187,F188",help="Sallitut DID:t pilkuilla: F190,F187,F188")
    ch=sub.add_parser("chrysler-300",help="Chrysler 300 / 300C / 300M -vuosimallitietokanta")
    ch.add_argument("--year",type=int,help="Mallivuosi")
    sub.add_parser("doctor",help="Tarkista ohjelmiston perustiedot")
    args=parser.parse_args(argv)
    if args.command=="chrysler-300":
        print(json.dumps(chrysler300_catalog(args.year),ensure_ascii=False,indent=2))
    elif args.command=="ecu-read":
        try:
            dids=parse_dids(args.dids.split(","))
            if args.demo:
                result=read_demo_identification(dids)
            else:
                if not all((args.interface,args.tx_id,args.rx_id)):
                    parser.error("Oikea CAN-luku vaatii --interface, --tx-id ja --rx-id; testaa ensin --demo")
                with SocketCanDidReader(args.interface,args.tx_id,args.rx_id) as reader:
                    result=reader.read_many(dids)
            print(json.dumps({"demo":args.demo,"service":"UDS 0x22 read-only","data":result},ensure_ascii=False,indent=2))
        except (ValueError,UdsError) as exc:
            parser.error(str(exc))
    elif args.command=="inventory":
        print(json.dumps(analyze_inventory(args.file),ensure_ascii=False,indent=2))
    elif args.command=="doctor":
        try: import serial; ser="asennettu"
        except ImportError: ser="puuttuu: pip install -e '.[serial]'"
        print("OpenTech2 v0.2 | OBD-II/UDS: vain luku | OEM / security: ei toteutettu | pyserial:",ser)
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
