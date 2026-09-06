'use client'

import { useEffect, useState } from 'react'
import type { NewsArticle } from '../lib/types'

function timeLabel(value:string){
  const date=new Date(value)
  if(Number.isNaN(date.getTime()))return 'ESPN'
  const diff=Math.max(0,Date.now()-date.getTime())
  const hours=Math.floor(diff/3600000)
  if(hours<1)return 'ESPN · Just now'
  if(hours<24)return `ESPN · ${hours}h ago`
  const days=Math.floor(hours/24)
  return `ESPN · ${days}d ago`
}

export default function HomeFantasyNews(){
  const [articles,setArticles]=useState<NewsArticle[]>([])

  useEffect(()=>{
    let cancelled=false
    fetch('/api/news?fantasy=1&limit=4',{cache:'no-store'})
      .then(r=>r.ok?r.json():null)
      .then(data=>{if(!cancelled)setArticles((data?.articles||[]).slice(0,4))})
      .catch(()=>{if(!cancelled)setArticles([])})
    return()=>{cancelled=true}
  },[])

  if(!articles.length)return null

  return <section className="og-fantasy-news" aria-label="ESPN fantasy football news">
    <header><div><b>Fantasy News</b><small>Top ESPN stories</small></div><span>ESPN</span></header>
    <div className="og-fantasy-news-list">
      {articles.map((article,index)=><a key={`${article.url}-${index}`} className="og-fantasy-news-row" href={article.url} target="_blank" rel="noreferrer" aria-label={`Read on ESPN: ${article.headline}`}>
        <span className="og-fantasy-news-thumb">{article.image?<img src={article.image} alt="" loading="lazy"/>:<span aria-hidden="true">ESPN</span>}</span>
        <span className="og-fantasy-news-copy"><b>{article.headline}</b><small>{timeLabel(article.published)}</small></span>
      </a>)}
    </div>
  </section>
}
