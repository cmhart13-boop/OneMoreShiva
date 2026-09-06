const BASE='https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl';
for (let season=2016; season<=2025; season++) {
  const url=`${BASE}/seasons/${season}/segments/0/leagues/1506903?view=mSettings&view=mTeam&view=mRoster&view=mMatchup&view=mMatchupScore&view=mDraftDetail&view=mStatus`;
  try {
    const r=await fetch(url,{headers:{Accept:'application/json','User-Agent':'Mozilla/5.0'}});
    console.log('ESPN_STATUS',season,r.status);
    if(!r.ok) continue;
    const d=await r.json();
    const teams=(d?.teams||[]).map(t=>({id:t.id,name:t.name,owners:t.owners,rank:t.rankCalculatedFinal,seed:t.playoffSeed,points:t.points}));
    console.log('ESPN_S2_CHAMP',season,JSON.stringify(teams.filter(t=>Number(t.rank)===1)));
  } catch(e) { console.log('ESPN_ERR',season,String(e)); }
}