const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
export function token(){return localStorage.getItem("foodguard_token") || ""}
export async function api(path:string, options:RequestInit={}) {
  const headers:any={"Content-Type":"application/json",...(options.headers||{})};
  if(token()) headers.Authorization=`Bearer ${token()}`;
  const res=await fetch(BASE+path,{...options,headers});
  if(!res.ok){let msg="Request failed";try{const d=await res.json();msg=d.detail||msg}catch{} throw new Error(msg)}
  const type=res.headers.get("content-type")||"";
  return type.includes("application/json")?res.json():res.text();
}
export const API_BASE=BASE;
