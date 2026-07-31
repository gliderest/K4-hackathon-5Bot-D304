"""Prototype adapters. Mock is for tests only; HTTP endpoint is never hardcoded."""
import json, os, time, urllib.request

class MockClient:
    def ask(self, input_text, context=""):
        return {"output":"[MOCK] Chưa có prototype API.","citations":[],"latency_ms":0,"http_status":200}

class HTTPClient:
    def __init__(self):
        self.url=os.environ["AI_API_URL"]; self.method=os.getenv("AI_API_METHOD","POST"); self.timeout=float(os.getenv("AI_API_TIMEOUT","30"))
    def ask(self,input_text,context=""):
        body=json.dumps({"input":input_text,"context":context}).encode(); req=urllib.request.Request(self.url,body,method=self.method,headers={"Content-Type":"application/json"})
        if os.getenv("AI_API_KEY"): req.add_header("Authorization",f"Bearer {os.environ['AI_API_KEY']}")
        started=time.perf_counter()
        with urllib.request.urlopen(req,timeout=self.timeout) as response:
            data=json.loads(response.read().decode())
            return {"output":data.get(os.getenv("AI_OUTPUT_FIELD","output"),""),"citations":data.get(os.getenv("AI_CITATIONS_FIELD","citations"),[]),"latency_ms":round((time.perf_counter()-started)*1000,2),"http_status":response.status}
