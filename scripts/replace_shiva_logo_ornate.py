from pathlib import Path
import re, ast
p=Path(__file__).resolve().parents[1]/'app_core.py'
s=p.read_text(encoding='utf-8')
mark=r'''SHIVA_MARK = r"""<svg class="shiva-trophy-mark" viewBox="0 0 120 168" aria-label="The Shiva trophy" role="img" xmlns="http://www.w3.org/2000/svg">
<defs>
 <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff0a8"/><stop offset=".22" stop-color="#d6a93e"/><stop offset=".52" stop-color="#7d531b"/><stop offset=".72" stop-color="#e7c76b"/><stop offset="1" stop-color="#6e4618"/></linearGradient>
 <linearGradient id="wood" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8b5a31"/><stop offset=".35" stop-color="#4a2b17"/><stop offset=".7" stop-color="#2b170d"/><stop offset="1" stop-color="#704522"/></linearGradient>
 <linearGradient id="marble" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#143b32"/><stop offset=".35" stop-color="#2d6a55"/><stop offset=".55" stop-color="#0d241f"/><stop offset=".8" stop-color="#397563"/><stop offset="1" stop-color="#102c26"/></linearGradient>
 <linearGradient id="silver" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f2ea"/><stop offset=".35" stop-color="#a9aca8"/><stop offset=".63" stop-color="#656b6d"/><stop offset="1" stop-color="#d8d8d1"/></linearGradient>
 <radialGradient id="portrait" cx="45%" cy="32%" r="70%"><stop offset="0" stop-color="#d7b090"/><stop offset=".55" stop-color="#b88166"/><stop offset="1" stop-color="#76513f"/></radialGradient>
 <filter id="shadow"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity=".55"/></filter>
</defs>
<g filter="url(#shadow)">
 <!-- ornate portrait crown -->
 <path d="M33 6h54l5 7-4 42H32l-4-42z" fill="url(#wood)" stroke="url(#gold)" stroke-width="3"/>
 <path d="M38 12h44l3 5-3 32H38l-3-32z" fill="#111518" stroke="#c89637" stroke-width="2"/>
 <path d="M31 10l-7 3 5 5-5 6 7 2M89 10l7 3-5 5 5 6-7 2" fill="none" stroke="#d7b65d" stroke-width="2"/>
 <path d="M39 16h42v29H39z" fill="url(#portrait)"/>
 <!-- Shiva portrait -->
 <ellipse cx="60" cy="28" rx="9.2" ry="10.8" fill="#b77c61"/>
 <path d="M48 31c1-14 5-19 12-19 9 0 13 8 13 19-2-3-4-4-6-5-1 5-4 8-7 8-5 0-7-4-8-8-1 2-2 3-4 5z" fill="#251915"/>
 <path d="M52 39c3-5 6-7 8-7 3 0 7 2 9 7v6H52z" fill="#263d54"/>
 <path d="M54.5 27h4.5M61 27h4.5" stroke="#201816" stroke-width="1.5"/><path d="M59 27h2" stroke="#201816" stroke-width="1"/>
 <path d="M57 32c2 1 4 1 6 0" fill="none" stroke="#6e302e" stroke-width="1"/>
 <!-- gold portrait ornaments -->
 <path d="M34 15c-8 4-9 12-4 20M86 15c8 4 9 12 4 20" fill="none" stroke="#cda54c" stroke-width="2.2"/>
 <circle cx="31" cy="39" r="3" fill="url(#gold)"/><circle cx="89" cy="39" r="3" fill="url(#gold)"/>
 <!-- THE SHIVA plaque directly under portrait -->
 <path d="M24 55h72l-5 17H29z" fill="url(#gold)" stroke="#5b3914" stroke-width="1.8"/>
 <path d="M31 59h58v9H31z" rx="2" fill="#23170e" stroke="#f0d27b" stroke-width="1"/>
 <text x="60" y="66.1" text-anchor="middle" font-family="Georgia,serif" font-size="8.2" font-weight="900" letter-spacing="1" fill="#f5dda0">THE SHIVA</text>
 <!-- top wooden shelf -->
 <path d="M13 72h94l-5 11H18z" fill="url(#wood)" stroke="#b17b3d" stroke-width="2"/>
 <path d="M17 76h86" stroke="#e0b965" stroke-width="1" opacity=".7"/>
 <!-- four trophy columns, green marble with gold caps -->
 <g>
  <path d="M20 83h13v48H20z" fill="url(#gold)" stroke="#6d491a"/><path d="M23 88h7v38h-7z" fill="url(#marble)" stroke="#ba9849" stroke-width="1"/>
  <path d="M87 83h13v48H87z" fill="url(#gold)" stroke="#6d491a"/><path d="M90 88h7v38h-7z" fill="url(#marble)" stroke="#ba9849" stroke-width="1"/>
  <path d="M36 85h8v43h-8z" fill="url(#gold)" opacity=".78"/><path d="M76 85h8v43h-8z" fill="url(#gold)" opacity=".78"/>
  <path d="M18 82h17v5H18zM85 82h17v5H85zM18 127h17v5H18zM85 127h17v5H85z" fill="url(#gold)"/>
 </g>
 <!-- center football player, helmet, ball, body -->
 <g transform="translate(0,-1)">
  <circle cx="61" cy="94" r="7.5" fill="url(#silver)" stroke="#494f50" stroke-width="1.2"/>
  <path d="M54 94c2-8 12-10 16-3l-3 7h-11z" fill="#a4a8a5" stroke="#4b5051"/>
  <path d="M67 92l7 1-1 5-7-1" fill="none" stroke="#474d4f" stroke-width="1.2"/>
  <path d="M58 101c-7 5-8 15-3 24h13c4-10 3-18-4-24z" fill="url(#silver)" stroke="#4a5052" stroke-width="1.2"/>
  <path d="M57 104l-10 8M66 103l8-10" stroke="#aeb2af" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="77" cy="89" rx="5" ry="3" transform="rotate(-28 77 89)" fill="#8a4d23" stroke="#d49a62" stroke-width="1"/>
  <path d="M59 124l-7 9M66 124l7 9" stroke="#858b8c" stroke-width="5" stroke-linecap="round"/>
 </g>
 <!-- cup beneath player -->
 <path d="M49 120h22c-1 10-5 14-11 14s-10-4-11-14z" fill="url(#gold)" stroke="#7e541b" stroke-width="1.5"/>
 <path d="M50 123c-8-1-9 7-4 9M70 123c8-1 9 7 4 9" fill="none" stroke="#cf9d35" stroke-width="2.5"/>
 <path d="M58 134h4v5h-4zM51 139h18v4H51z" fill="url(#gold)"/>
 <!-- layered heavy wooden base -->
 <path d="M12 132h96l-4 10H16z" fill="url(#wood)" stroke="#a87336" stroke-width="2"/>
 <path d="M18 142h84l7 10H11z" fill="#3a2112" stroke="#7e502a" stroke-width="2"/>
 <path d="M24 146h72v7H24z" fill="#151515" stroke="#c69c48" stroke-width="1.2"/>
 <text x="60" y="151.4" text-anchor="middle" font-family="Georgia,serif" font-size="5.8" font-weight="900" letter-spacing="1.2" fill="#f0d27b">SHIVA</text>
 <path d="M8 152h104l-5 11H13z" fill="url(#wood)" stroke="#8e5d30" stroke-width="2"/>
 <path d="M19 157h82" stroke="#d2a54f" stroke-width="1" opacity=".55"/>
</g></svg>"""'''
ns=re.sub(r'SHIVA_MARK = r""".*?</svg>"""',mark,s,count=1,flags=re.S)
if ns==s: raise SystemExit('SHIVA_MARK replacement failed')
# Make the ornate mark large enough to read while staying compact in the app header.
ns=ns.replace('.brand-badge{width:49px!important;height:58px!important;', '.brand-badge{width:58px!important;height:72px!important;')
ns=ns.replace('.shiva-trophy-mark{display:block!important;width:47px!important;height:57px!important}', '.shiva-trophy-mark{display:block!important;width:56px!important;height:70px!important}')
p.write_text(ns,encoding='utf-8')
ast.parse(ns)
print('ORNATE SHIVA LOGO INSTALLED')
