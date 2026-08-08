"""Bite-size 2026 full-PPR draft intelligence for the Shiva 2026 Draft Guide.
Only redraft/full-PPR-relevant material is represented here. Half-PPR boards/projections and dynasty rankings are intentionally excluded.
"""

PPR_BIG_BOARD = {
"Jahmyr Gibbs":1,"Bijan Robinson":2,"Ja'Marr Chase":3,"Puka Nacua":4,"Christian McCaffrey":5,"Amon-Ra St. Brown":6,"Jaxon Smith-Njigba":7,"Jonathan Taylor":8,"James Cook III":9,"CeeDee Lamb":10,"Omarion Hampton":11,"Ashton Jeanty":12,"Justin Jefferson":13,"Chase Brown":14,"Kenneth Walker III":15,"Saquon Barkley":16,"Drake London":17,"De'Von Achane":18,"Brock Bowers":19,"A.J. Brown":20,"George Pickens":21,"Rashee Rice":22,"Nico Collins":23,"Derrick Henry":24,"Trey McBride":25,"Jeremiyah Love":26,"DeVonta Smith":27,"Malik Nabers":28,"Josh Allen":29,"Chris Olave":30,"Josh Jacobs":31,"Tee Higgins":32,"Breece Hall":33,"Jaylen Waddle":34,"Zay Flowers":35,"Kyren Williams":36,"Tetairoa McMillan":37,"Emeka Egbuka":38,"Luther Burden III":39,"Colston Loveland":40,"Javonte Williams":41,"Garrett Wilson":42,"Ladd McConkey":43,"DJ Moore":44,"Cam Skattebo":45,"Bucky Irving":46,"Travis Etienne Jr.":47,"Tyler Warren":48,"Terry McLaurin":49,"Lamar Jackson":50,
"Rome Odunze":51,"Davante Adams":52,"David Montgomery":53,"Christian Watson":54,"Bhayshul Tuten":55,"D'Andre Swift":56,"TreVeyon Henderson":57,"Quinshon Judkins":58,"Drake Maye":59,"Jayden Daniels":60,"Mike Evans":61,"Parker Washington":62,"Joe Burrow":63,"Jalen Hurts":64,"Jameson Williams":65,"Carnell Tate":66,"Brian Thomas Jr.":67,"Chuba Hubbard":68,"Jadarian Price":69,"Sam LaPorta":70,"Harold Fannin Jr.":71,"Marvin Harrison Jr.":72,"Jordyn Tyson":73,"Alec Pierce":74,"Rhamondre Stevenson":75,"Tucker Kraft":76,"Caleb Williams":77,"Justin Herbert":78,"Trevor Lawrence":79,"Jaylen Warren":80,"Rico Dowdle":81,"RJ Harvey":82,"Kyle Pitts Sr.":83,"Makai Lemon":84,"Michael Wilson":85,"Jaxson Dart":86,"Brock Purdy":87,"Dak Prescott":88,"Chris Godwin Jr.":89,"Tony Pollard":90,"Jonathon Brooks":91,"Blake Corum":92,"DK Metcalf":93,"George Kittle":94,"Josh Downs":95,"Stefon Diggs":96,"Courtland Sutton":97,"Kyle Monangai":98,"Rachaad White":99,"J.K. Dobbins":100,"Dalton Kincaid":101,"Bo Nix":102,"Patrick Mahomes II":103,"Matthew Stafford":104,"Kyler Murray":105,"Jared Goff":106,"Deebo Samuel Sr.":107,"Quentin Johnston":108,"Jordan Addison":109,"Malik Willis":110,"Jakobi Meyers":111,"Michael Pittman Jr.":112,"Kenny Gainwell":113,"Jordan Mason":114,"Jacory Croskey-Merritt":115,"Dallas Goedert":116,"Mark Andrews":117,"Tyler Shough":118,"Zach Charbonnet":119,"Chris Rodriguez Jr.":120,"Jayden Reed":121,"Romeo Doubs":122,"Isaiah Likely":123,"Matthew Golden":124,"Aaron Jones Sr.":125,"Baker Mayfield":126,"Jake Ferguson":127,"Jordan Love":128,"Keaton Mitchell":129,"Travis Kelce":130,"Isiah Pacheco":131,"Cam Ward":132,"Tank Bigsby":133,"Tyler Allgeier":134,"De'Zhaun Stribling":135,"Wan'Dale Robinson":136,"Xavier Worthy":137,"Oronde Gadsden II":138,"Alvin Kamara":139,"Ray Davis":140,"Chig Okonkwo":141,"Tyrone Tracy Jr.":142,"Sam Darnold":143,"Woody Marks":144,"Jayden Higgins":145,"KC Concepcion":146,"Travis Hunter":147,"Tre Tucker":148,"Tyjae Spears":149,"Bryce Young":150}

# Page 5 target/pass/avoid color coding from the PPR positional board.
TARGETS = {"Jahmyr Gibbs","Omarion Hampton","Chase Brown","Kenneth Walker III","Kyren Williams","Travis Etienne Jr.","Bhayshul Tuten","Chuba Hubbard","Jaylen Warren","Tony Pollard","Jonathon Brooks","Jacory Croskey-Merritt","Ray Davis","Caleb Williams","Justin Herbert","Trevor Lawrence","Brock Purdy","Kyler Murray","Malik Willis","DeVonta Smith","Jaylen Waddle","Zay Flowers","Luther Burden III","Terry McLaurin","Parker Washington","Chris Godwin Jr.","Josh Downs","Brock Bowers","Colston Loveland","Tyler Warren","Dalton Kincaid","Dallas Goedert","Terrance Ferguson"}
PASSES = {"Travis Etienne Jr.","Tony Pollard","J.K. Dobbins","Chris Olave","Marvin Harrison Jr.","Michael Pittman Jr.","Jakobi Meyers","Trey McBride","Jake Ferguson"}
AVOIDS = {"De'Von Achane","Quinshon Judkins","RJ Harvey","Aaron Jones Sr.","DK Metcalf","Courtland Sutton","Jordan Love","Travis Kelce"}

PPR_RECEPTION_SHARE = {
"Michael Pittman Jr.":41.7,"Josh Downs":41.5,"Garrett Wilson":41.1,"Stefon Diggs":39.4,"Chris Godwin Jr.":38.6,"Malik Nabers":38.4,"Jakobi Meyers":38.0,"Chris Olave":38.0,"Rashee Rice":36.5,"Amon-Ra St. Brown":36.1,
"Tyjae Spears":33.5,"Kenny Gainwell":31.2,"Jaylen Warren":25.9,"Rachaad White":25.4,"Chase Brown":23.2,"Javonte Williams":23.1,"Breece Hall":22.9,"RJ Harvey":22.7,"Christian McCaffrey":21.5,"De'Von Achane":21.1,"Bijan Robinson":20.7,"Bucky Irving":20.1,
"Jake Ferguson":45.1,"T.J. Hockenson":44.7,"Travis Kelce":43.8,"Trey McBride":42.6,"Dalton Kincaid":41.4}

ADJ_PPG = {"Christian McCaffrey":24.8,"Jahmyr Gibbs":24.6,"Jonathan Taylor":23.8,"Bijan Robinson":22.0,"Chase Brown":21.0,"De'Von Achane":20.4,"Cam Skattebo":19.1,"Josh Jacobs":18.0,"James Cook III":17.9,"Derrick Henry":16.9,"Javonte Williams":16.2,"Omarion Hampton":16.2,"Travis Etienne Jr.":15.4,"Kyren Williams":14.7,"Saquon Barkley":14.6,"Ashton Jeanty":14.5,"Puka Nacua":23.7,"Jaxon Smith-Njigba":20.4,"Amon-Ra St. Brown":20.3,"Ja'Marr Chase":20.1,"Drake London":19.7,"Rashee Rice":18.8,"Chris Olave":18.8,"CeeDee Lamb":16.6,"George Pickens":16.1,"Rome Odunze":15.5,"Davante Adams":15.3,"Tee Higgins":15.2,"Nico Collins":15.0,"Zay Flowers":15.0,"Josh Allen":23.2,"Drake Maye":19.8,"Caleb Williams":18.7,"Jalen Hurts":18.3,"Joe Burrow":18.2,"Lamar Jackson":17.5,"Trey McBride":18.6,"Brock Bowers":16.4,"Tucker Kraft":16.2,"George Kittle":15.4}

PLAYER_INTEL = {
"Christian McCaffrey":"Four of the five best PPR RB seasons since he entered the NFL belong to CMC; Shiva flags unmatched ceiling.",
"Puka Nacua":"36.8% targets per route since 2024; no other qualified player is above 30%.",
"Dalton Kincaid":"Led TEs across a huge group of 2025 route/target efficiency measures; the missing ingredient was route volume.",
"Chase Brown":"Cincinnati QBs were the top three in checkdown rate in 2025, a strong PPR fit for Brown.",
"Parker Washington":"454 receiving yards over Jacksonville's final four games, more than Brian Thomas Jr. and Jakobi Meyers combined despite fewer routes.",
"Trey McBride":"Ran 667 routes in 2025, more than any WR; Ja'Marr Chase was second overall at 613.",
"Tyler Warren":"Targets per route rose from 21% with Michael Pittman on the field to 30% without him.",
"Kenneth Walker III":"Shiva flags 2.0+ combined goal-line carries and red-zone targets as elite RB opportunity territory and sees that type of ceiling for Walker.",
"Chuba Hubbard":"Shiva flags 2.0+ combined goal-line carries and red-zone targets as elite RB opportunity territory and sees that type of ceiling for Hubbard.",
"Rome Odunze":"55% of his 2025 end-zone targets were deemed inaccurate; DJ Moore also vacated 13 end-zone targets.",
"Luther Burden III":"Ranked 8th among WRs in fantasy points per snap as a rookie; six of the seven ahead of him were fantasy WR1s.",
"Ja'Marr Chase":"Exactly 200 targets across his last 17 games with Joe Burrow.",
"Tetairoa McMillan":"Had 16 targets lost to drops/WR error as a rookie, tied for most in the NFL; Shiva expects positive regression.",
"Josh Allen":"Has finished top-two in QB fantasy points in six straight seasons; no other QB has done it twice in that span.",
"Jalen Hurts":"All four of his previous playcallers gave the QB more than 40% of team goal-line carries; 2026 brings a fifth playcaller.",
"Jahmyr Gibbs":"Was 2nd in yards per attempt on gap runs but 42nd on zone runs in 2025; his new OC has a history of heavy gap usage.",
"Jadarian Price":"College pass-blocking grade was 38.5; pass protection is a potential obstacle to receiving-down work.",
"Jaylen Warren":"Top-two among RBs in targets/route, yards/route and missed tackles per reception in 2025; Pittsburgh has 82 vacated RB targets.",
"De'Von Achane":"Career receiving PPG with Tua: 11.4; without Tua across eight games: 3.4. Major PPR dependency flag.",
"Ladd McConkey":"Yards per route rose 96% with motion; Mike McDaniel's offense uses motion at the league's highest rate.",
"CeeDee Lamb":"Shiva Luck Metric rated Lamb the unluckiest player of 2025, estimating about 2.7 PPG lost to bad luck.",
"Drake Maye":"QB1 in quarters 1-3 last season but QB32 in fourth quarters; game script is a key 2026 variable.",
"Ashton Jeanty":"Recent top-12 NFL-drafted RBs have a strong Year-2 breakout history; Shiva highlights Jeanty as a sophomore RB1 candidate.",
"Omarion Hampton":"Recent top-25 NFL-drafted RBs have an exceptional record of producing an RB1 season by Year 2; Hampton fits that breakout profile.",
"Lamar Jackson":"Had five passing TDs dropped in 2025 despite only 13 games and the league's lowest pass attempts per game.",
"Travis Kelce":"Fantasy PPG has declined three straight seasons and he ranked 28th among TEs in red-zone target share in 2025.",
"Zay Flowers":"Produced 4.83 yards/route on play action, second among WRs; his new offensive environment projects much more play action.",
"Davante Adams":"His 2025 end-zone-target scoring rate was historically extreme, creating regression risk.",
"Malik Willis":"5th in fantasy points per snap among QBs since 2023 and 1st in 2025; rushing/efficiency makes him a late-QB upside archetype."}

DRAFT_RULES = [
"Use rankings with ADP: don't pay a player's rank when the market lets you draft him later.",
"Prioritize upside over merely beating positional ADP.",
"Shiva's median 12-team PPR build starts RB-RB, then targets WR in Rounds 3 and 5 while staying BPA-aware.",
"Aim to leave the early/middle draft with roughly three RBs from the top 25-30 range; Shiva views RB30-40 as weaker value than nearby QB/WR/TE.",
"QB sweet spot: target the QB7-11 ADP range, often around Round 8; late rushing QBs are the secondary plan.",
"Late WR upside is attractive: target talent plus major role/environment change or uncertainty.",
"At TE, take value when it falls, grab the last useful mid-round tier around Rounds 7-8, or punt intentionally.",
"Prefer backup-RB/handcuff upside over a TE2; save K and D/ST for the final two rounds.",
"Balance correlated risk; don't stack too many fragile/high-variance bets on one roster.",
"Early and post-draft waivers matter disproportionately, so keep roster flexibility." ]

def player_payload(name):
    return {"rank":PPR_BIG_BOARD.get(name),"tag":"TARGET" if name in TARGETS else "AVOID" if name in AVOIDS else "PASS" if name in PASSES else None,"ppr_rec_share":PPR_RECEPTION_SHARE.get(name),"adj_ppg":ADJ_PPG.get(name),"intel":PLAYER_INTEL.get(name)}

def shiva_context(names):
    rows=[]
    for name in names:
        d=player_payload(name)
        bits=[]
        if d["rank"]: bits.append(f"Shiva PPR rank #{d['rank']}")
        if d["tag"]: bits.append(d["tag"])
        if d["adj_ppg"] is not None: bits.append(f"2025 adjusted PPG {d['adj_ppg']}")
        if d["ppr_rec_share"] is not None: bits.append(f"{d['ppr_rec_share']}% of points via receptions")
        if d["intel"]: bits.append(d["intel"])
        if bits: rows.append(name+": "+"; ".join(bits))
    return " | ".join(rows)
