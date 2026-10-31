# Optional USB serial-to-Wi-Fi API bridge. pip install pyserial requests
import argparse, json, serial, requests
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--port",required=True); p.add_argument("--baud",type=int,default=115200)
    p.add_argument("--url",required=True); p.add_argument("--device-id",required=True); p.add_argument("--device-key",required=True)
    a=p.parse_args()
    with serial.Serial(a.port,a.baud,timeout=2) as ser:
        print("USB serial bridge listening; Ctrl+C to stop")
        while True:
            line=ser.readline().decode("utf-8","ignore").strip()
            if not line: continue
            try:
                payload=json.loads(line)
                response=requests.post(a.url.rstrip("/")+"/api/sensors/ingest",json=payload,
                  headers={"X-Device-ID":a.device_id,"X-Device-Key":a.device_key},timeout=8)
                print(response.status_code,response.text)
            except Exception as exc: print("Bridge error:",exc)
if __name__=="__main__": main()
