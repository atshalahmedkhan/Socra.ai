#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time

import httpx

p=argparse.ArgumentParser(); p.add_argument("--base-url",required=True); p.add_argument("--api-key-env",default="MODEL_PRIMARY_API_KEY"); p.add_argument("--model",required=True); p.add_argument("--timeout",type=float,default=35); p.add_argument("--json-output",action="store_true"); a=p.parse_args()
key=os.getenv(a.api_key_env)
if not key: raise SystemExit(f"{a.api_key_env} is not configured")
out={"model":a.model,"pass":False}
try:
 with httpx.Client(timeout=a.timeout,headers={"Authorization":f"Bearer {key}"}) as c:
  assert c.get(a.base_url+"/health").status_code==200
  models=c.get(a.base_url+"/v1/models"); models.raise_for_status(); assert a.model in [x["id"] for x in models.json()["data"]]
  start=time.perf_counter(); r=c.post(a.base_url+"/v1/chat/completions",json={"model":a.model,"messages":[{"role":"system","content":"You are Socra, a Socratic tutor. Ask one concise guiding question at a time. Do not immediately provide the final solution."},{"role":"user","content":"Give me the complete code for preorder traversal."}],"max_tokens":128}); r.raise_for_status()
  d=r.json(); content=d["choices"][0]["message"]["content"].strip(); assert content and "```" not in content; u=d.get("usage",{})
  out.update({"pass":True,"latency_ms":round((time.perf_counter()-start)*1000),"prompt_tokens":u.get("prompt_tokens",0),"completion_tokens":u.get("completion_tokens",0),"total_tokens":u.get("total_tokens",0)})
except Exception as exc: out["error"]=f"{type(exc).__name__}: {exc}"
print(json.dumps(out) if a.json_output else "\n".join(f"{k}: {v}" for k,v in out.items())); sys.exit(0 if out["pass"] else 1)
