from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')

# Add clean, legible answer styles before the mobile media rule.
needle='@media(max-width:430px){.stat-strip'
css=r'''
/* Shiva answer presentation: readable summary first, details tucked into ESPN-style drawers. */
.shiva-answer-summary{margin:13px 0 9px;padding:14px 14px 13px;border-left:3px solid rgba(93,199,151,.62);border-radius:10px;background:linear-gradient(100deg,rgba(38,82,68,.22),rgba(13,24,32,.20) 58%,transparent);color:#f5f8fa;font-size:16px;line-height:1.55;font-weight:650;letter-spacing:-.08px}
.shiva-answer-summary b,.shiva-answer-summary strong{color:#fff;font-weight:900}
.shiva-answer-label{display:block;margin-bottom:6px;color:#86d9b3;font-size:10px;line-height:1;font-weight:950;letter-spacing:.8px;text-transform:uppercase}
.st-key-home_shiva_card details,.st-key-shiva_page_card details{margin:6px 0!important;border:1px solid rgba(104,126,143,.25)!important;border-radius:11px!important;background:linear-gradient(145deg,rgba(18,31,41,.74),rgba(10,19,27,.78))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025)!important;overflow:hidden!important}
.st-key-home_shiva_card details summary,.st-key-shiva_page_card details summary{padding:11px 12px!important;color:#e7edf2!important;font-size:13px!important;font-weight:900!important;letter-spacing:.05px!important}
.st-key-home_shiva_card details [data-testid="stMarkdownContainer"],.st-key-shiva_page_card details [data-testid="stMarkdownContainer"]{padding:0 12px 10px!important}
.st-key-home_shiva_card details p,.st-key-home_shiva_card details li,.st-key-shiva_page_card details p,.st-key-shiva_page_card details li{font-size:14px!important;line-height:1.52!important;color:#c8d2da!important}
.st-key-home_shiva_card details ul,.st-key-home_shiva_card details ol,.st-key-shiva_page_card details ul,.st-key-shiva_page_card details ol{padding-left:20px!important;margin-top:5px!important}
'''
if needle in s and '/* Shiva answer presentation:' not in s:
    s=s.replace(needle,css+'\n'+needle,1)

start=s.index('def _ask_shiva_widget(prefix:str):')
end=s.index("\n'''\nsource = source[:ask_start]",start)
new=r'''def _shiva_answer_sections(text:str)->dict:
    raw=str(text or "").strip()
    sections={"short":"","why":"","exceptions":"","checklist":""}
    if not raw:return sections
    lines=[x.strip() for x in raw.splitlines() if x.strip()]
    current="short"
    for line in lines:
        clean=re.sub(r"^[#*\-\s]+","",line).strip()
        low=clean.casefold().rstrip(":")
        if low.startswith("short answer"):
            current="short";rest=clean.split(":",1)[1].strip() if ":" in clean else ""
            if rest:sections[current]+=("\n" if sections[current] else "")+rest
            continue
        if low.startswith("why") or low.startswith("quick rule") or low.startswith("additional information"):
            current="why";rest=clean.split(":",1)[1].strip() if ":" in clean else ""
            if rest:sections[current]+=("\n" if sections[current] else "")+rest
            continue
        if low.startswith("exception"):
            current="exceptions";rest=clean.split(":",1)[1].strip() if ":" in clean else ""
            if rest:sections[current]+=("\n" if sections[current] else "")+rest
            continue
        if "checklist" in low or low.startswith("before you pick") or low.startswith("actionable"):
            current="checklist";rest=clean.split(":",1)[1].strip() if ":" in clean else ""
            if rest:sections[current]+=("\n" if sections[current] else "")+rest
            continue
        sections[current]+=("\n" if sections[current] else "")+line
    if not sections["short"]:
        sections["short"]=raw
    return sections

def _ask_shiva_widget(prefix:str):
    q=st.text_area("Ask Shiva",placeholder="Ask about players, PPR history, rankings, your roster, or who to draft…",height=92,key=f"{prefix}_q",label_visibility="collapsed")
    if st.button("✦ GET SHIVA'S ANSWER",type="primary",use_container_width=True,key=f"{prefix}_go") and q.strip():
        with st.spinner("Reading Shiva's internal data…"):
            result=ask_shiva_full(q.strip())
        st.session_state[f"{prefix}_result"]={"question":q.strip(),**result}
        hist=st.session_state.get("ask_history",[])
        hist.insert(0,st.session_state[f"{prefix}_result"]);st.session_state["ask_history"]=hist[:12]
    item=st.session_state.get(f"{prefix}_result")
    if item:
        parts=_shiva_answer_sections(item.get("answer",""))
        short=parts.get("short","").strip()
        # Keep the default view fast: cap an unstructured response to its first useful paragraph/sentences.
        if "\n" in short and not any(parts.get(k) for k in ("why","exceptions","checklist")):
            chunks=[x.strip() for x in short.split("\n") if x.strip()]
            short=chunks[0] if chunks else short
        st.markdown(f'<div class="shiva-answer-summary"><span class="shiva-answer-label">Short answer</span>{html.escape(short).replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
        why=parts.get("why","").strip()
        exceptions=parts.get("exceptions","").strip()
        checklist=parts.get("checklist","").strip()
        # If an older/unstructured answer has no drawers yet, keep Shiva's calculation details available under Why & Quick Rules rather than dumping them on-screen.
        if not why:
            why=str(item.get("method") or "Shiva used the app’s internal data first, then summarized the result for the current question.")
        if not exceptions:
            exceptions="No specific exceptions were identified for this answer."
        if not checklist:
            checklist="Use the short answer as the default call, then check current roster construction, available-player value, and any late-breaking role or injury news before you pick."
        with st.expander("Why & Quick Rules",expanded=False):st.markdown(why)
        with st.expander("Exceptions",expanded=False):st.markdown(exceptions)
        with st.expander("Actionable Checklist",expanded=False):st.markdown(checklist)
        with st.expander("See Shiva's data",expanded=False):_render_shiva_work(item,prefix)
'''
s=s[:start]+new+s[end:]

# Make the AI itself return the exact four-part structure so the UI can place content reliably.
old='system="You are Shiva, an elite fantasy-football analyst. ESPN full 1-point PPR is the default. INTERNAL APP DATA IS AUTHORITATIVE. Never alter, invent, or contradict supplied numbers. If internal evidence answers the question, explain it clearly and concisely. If it does not, say what is uncertain."'
new_system='system="You are Shiva, an elite fantasy-football analyst. ESPN full 1-point PPR is the default. INTERNAL APP DATA IS AUTHORITATIVE. Never alter, invent, or contradict supplied numbers. Return exactly four concise sections with these headings: SHORT ANSWER, WHY & QUICK RULES, EXCEPTIONS, ACTIONABLE CHECKLIST. SHORT ANSWER must be 2-3 sentences maximum and lead with the recommendation. Put supporting detail in WHY & QUICK RULES. Put caveats only in EXCEPTIONS. Put concrete next steps only in ACTIONABLE CHECKLIST. Keep mobile readability high; avoid giant paragraphs. If internal evidence does not answer the question, clearly say what is uncertain."'
if old in s:s=s.replace(old,new_system,1)

p.write_text(s,encoding='utf-8')
