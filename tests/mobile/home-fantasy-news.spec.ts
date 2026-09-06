import { expect, test } from '@playwright/test'

test('home shows four linked ESPN fantasy stories with thumbnails below dashboard',async({page})=>{
  await page.route('**/api/auth/session',route=>route.fulfill({status:401,contentType:'application/json',body:'{}'}))
  await page.route('**/api/leagues',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[]})}))
  await page.route('**/api/scoreboard*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({games:[]})}))
  await page.route('**/api/defense-matchups*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({baselineSeason:2025,methodology:'test',source:'test',defenses:{}})}))
  await page.route('**/api/rankings*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({players:[
    {id:'1',espnId:'1',name:'Alpha Runner',team:'ATL',pos:'RB',rank:1,percentStarted:92,projectedPoints:20},
    {id:'2',espnId:'2',name:'Bravo Receiver',team:'BUF',pos:'WR',rank:2,percentStarted:71,projectedPoints:18},
    {id:'3',espnId:'3',name:'Charlie Tight End',team:'KC',pos:'TE',rank:3,percentStarted:55,projectedPoints:15},
    {id:'4',espnId:'4',name:'Delta Flex',team:'DET',pos:'WR',rank:4,percentStarted:41,projectedPoints:13},
    {id:'5',espnId:'5',name:'Echo Back',team:'LV',pos:'RB',rank:5,percentStarted:10,projectedPoints:8}
  ]})}))
  const articles=Array.from({length:4},(_,i)=>({headline:`Fantasy Story ${i+1}`,description:'Fantasy football lineup news',published:new Date(Date.now()-i*3600000).toISOString(),url:`https://www.espn.com/fantasy/story-${i+1}`,image:`https://example.com/thumb-${i+1}.jpg`}))
  await page.route('**/api/news*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({articles,source:'espn-live'})}))
  await page.route('https://example.com/**',route=>route.fulfill({status:200,contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR42mNk+M/wHwAF/gL+NqFrWQAAAABJRU5ErkJggg==','base64')}))
  await page.route('https://a.espncdn.com/**',route=>route.fulfill({status:200,contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR42mNk+M/wHwAF/gL+NqFrWQAAAABJRU5ErkJggg==','base64')}))

  await page.goto('/',{waitUntil:'networkidle'})
  const dashboard=page.locator('.og-snapshots')
  const news=dashboard.locator('.og-fantasy-news')
  await expect(news).toBeVisible()
  await expect(news.getByText('Fantasy News',{exact:true})).toBeVisible()
  const cards=news.locator('.og-fantasy-news-card')
  await expect(cards).toHaveCount(4)
  for(let i=0;i<4;i++){
    const card=cards.nth(i)
    await expect(card).toHaveAttribute('href',`https://www.espn.com/fantasy/story-${i+1}`)
    await expect(card).toHaveAttribute('target','_blank')
    await expect(card.locator('img')).toHaveAttribute('src',`https://example.com/thumb-${i+1}.jpg`)
    await expect(card).toContainText(`Fantasy Story ${i+1}`)
  }
  const dashboardBox=await page.locator('.og-snapshot-track').boundingBox()
  const newsBox=await news.boundingBox()
  expect(dashboardBox).not.toBeNull();expect(newsBox).not.toBeNull()
  expect(newsBox!.y).toBeGreaterThanOrEqual(dashboardBox!.y+dashboardBox!.height)
})
