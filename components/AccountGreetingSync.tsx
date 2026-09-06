'use client'

import { useEffect } from 'react'

function normalizeLabel(label:HTMLElement){
  const text=(label.textContent||'').trim()
  if(text==='Login / Sign Up') label.textContent='Sign In / Sign Up'
  else if(text.startsWith('Hi, ')) label.textContent=`Hey ${text.slice(4)}`
}

export default function AccountGreetingSync(){
  useEffect(()=>{
    const sync=()=>document.querySelectorAll<HTMLElement>('.account-button-label').forEach(normalizeLabel)
    sync()
    const observer=new MutationObserver(sync)
    observer.observe(document.body,{subtree:true,childList:true,characterData:true})
    return()=>observer.disconnect()
  },[])
  return null
}
