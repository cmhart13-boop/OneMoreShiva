export function parseCsvLine(line){const out=[];let value="",quoted=false;for(let i=0;i<line.length;i+=1){const ch=line[i];if(ch==='"'){if(quoted&&line[i+1]==='"'){value+='"';i+=1}else quoted=!quoted}else if(ch===','&&!quoted){out.push(value);value=""}else value+=ch}out.push(value);return out}
export function toNumber(v){if(v==null||v==='')return null;const n=Number(v);return Number.isFinite(n)?n:null}
export const normalizeName=v=>String(v||"").toLowerCase().replace(/[^a-z0-9]/g,"");
export function rowFrom(headers,line){const values=parseCsvLine(line);return Object.fromEntries(headers.map((h,i)=>[h,values[i]??""]))}
