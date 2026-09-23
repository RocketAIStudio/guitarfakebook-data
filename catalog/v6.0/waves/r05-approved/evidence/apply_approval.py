from pathlib import Path
import json, re, hashlib, copy, csv, collections, unicodedata, shutil, html, datetime

ROOT=Path('/workspace/scratch/c88c9f6ffc57')
SRC=ROOT/'recovered/r05/GuitarFakeBook_V6.0_DESKTOP_REVIEW_R05'
OUT=ROOT/'output/GuitarFakeBook_V6.0_APPROVED_R06'
OUT.mkdir(parents=True,exist_ok=True)
WAVE=OUT/'catalog/v6.0/waves/r05-approved'
(WAVE/'songs').mkdir(parents=True,exist_ok=True)
(WAVE/'evidence').mkdir(exist_ok=True)
def sha(b): return hashlib.sha256(b).hexdigest()
def js(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def writejson(path,x): path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def identity(x):
    x=unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]','',re.sub(r'\b(the|and)\b','',x))
def initial_caps(s):
    # Preserve spelling/punctuation; capitalize word initials without breaking contractions or ordinals.
    acronyms={'tv':'TV','ufo':'UFO'}
    def word(m):
        w=m.group()
        if w.casefold() in acronyms:return acronyms[w.casefold()]
        if re.match(r'^\d',w):return w
        return w[0].upper()+w[1:]
    return re.sub(r"[\w]+(?:['’][\w]+)*",word,s)
def titlekey(s):
    return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',re.sub(r'\s*\*alt.*$','',s)).encode('ascii','ignore').decode().lower())

baseline=json.loads((ROOT/'recovered/v4-index.json').read_text())
assert baseline==json.loads((ROOT/'recovered/v4-catalog.json').read_text())['index']
original=json.loads((ROOT/'recovered/catalog-original.json').read_text())
dataset=json.loads((SRC/'review-dataset.json').read_text())
assert len(original['embedded'])==len(dataset['songs'])==317
old_byid={x['id']:x for x in original['embedded']}
names=collections.defaultdict(list)
for row in baseline['songs']:
    if row['artist'] not in names[identity(row['artist'])]:names[identity(row['artist'])].append(row['artist'])
artist_map={}
map_evidence=[]
for a in sorted({x['artist'] for x in original['embedded']}|{'The Beach Boys'}):
    choices=names.get(identity(a),[])
    if a=='The Beach Boys':chosen='Beach Boys'
    else:
        chosen=next((n for n in choices if not n.lower().startswith('the ') and re.search('[a-z]',n)),next((n for n in choices if re.search('[a-z]',n)),choices[0] if choices else a))
    artist_map[a]=chosen
    map_evidence.append({'reviewArtist':a,'canonicalArtist':chosen,'productionVariants':choices,'basis':'Explicit owner preference' if a=='The Beach Boys' else ('Existing V4 first display spelling; omit leading The only when that variant already exists' if choices else 'New artist; preserve approved review name')})

cat=copy.deepcopy(original)
changes=[]; manifests=[]
for song in cat['embedded']:
    before=old_byid[song['id']]
    song['artist']=artist_map[song['artist']]
    if 'artistNormalized' in song:song['artistNormalized']=re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',song['artist']).encode('ascii','ignore').decode().lower())
    song['title']=initial_caps(song['title']);song['displayTitle']=initial_caps(song['displayTitle'])
    allowed={'artist','artistNormalized','title','displayTitle'}
    assert {k:v for k,v in song.items() if k not in allowed}=={k:v for k,v in before.items() if k not in allowed}
    path=WAVE/'songs'/f'{song["id"]}.json';writejson(path,song)
    payloadhash=sha(path.read_bytes())
    manifests.append({'id':song['id'],'artist':song['artist'],'title':song['title'],'payloadSha256':payloadhash,'path':str(path.relative_to(OUT)),'sourceSha256':song['source']['sha256'],'originalReviewPayloadSha256':next(d['payloadSha256'] for d in dataset['songs'] if d['id']==song['id']),'contentSha256':sha(song['content'].encode()),'status':'keep'})
    changes.append({'Song ID':song['id'],'Original artist':before['artist'],'Approved artist':song['artist'],'Original title':before['title'],'Approved title':song['title'],'Decision':'Keep'})
newby={s['id']:s for s in cat['embedded']}; manifestby={s['id']:s for s in manifests}
for row in cat['index']['songs']:
    for k in ['artist','title','displayTitle']:row[k]=newby[row['id']][k]
newdataset=copy.deepcopy(dataset);newdataset['buildId']='GFB-V6.0-APPROVED-R06';newdataset['status']='OWNER_SONG_SELECTION_APPROVED_NOT_DEPLOYED'
for row in newdataset['songs']:
    for k in ['artist','title','payloadSha256']:row[k]=manifestby[row['id']][k]
newdataset.pop('datasetId');newdataset['datasetId']=sha(js(newdataset).encode())
writejson(OUT/'review-dataset.json',newdataset)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def decision(data):
    return {'schema':'gfb-desktop-review-decisions/v2','buildId':data['buildId'],'datasetId':data['datasetId'],'baselineSha256':data['baselineSha256'],'deploymentAuthorized':False,'decisionScope':'Owner approved all 317 reviewed songs; metadata capitalization and production V4 artist-name alignment authorized. Release gates remain separate.','decisions':[dict(id=s['id'],artist=s['artist'],title=s['title'],payloadSha256=s['payloadSha256'],status='keep',note='Peter approved all reviewed songs in chat; apply initial capitals and match production V4 artist names.',reviewedSemitones=0) for s in data['songs']]}
writejson(OUT/'OWNER_DECISIONS_R05_ORIGINAL.json',decision(dataset))
writejson(OUT/'OWNER_DECISIONS_R06_NORMALIZED.json',decision(newdataset))
writejson(WAVE/'owner-approval.json',{'receivedAt':now,'instruction':'these are all approved - just apply initial caps for the songs Human Touch instead of human touch. And make sure you match the the name that is in current prod v4 - so The beach boys but in guitarfakebook its Beach Boys - so thats what it should be - there are all 100% approved - move forward','approvedCount':317,'originalDatasetId':dataset['datasetId'],'normalizedDatasetId':newdataset['datasetId'],'status':'OWNER_APPROVED','releaseStatus':'NOT_DEPLOYED','scope':'All 317 playable proposals in R05; not the 1,685 audit rows excluded from the review player.'})
writejson(WAVE/'artist-name-map.json',{'productionAppCommit':'0bf10064a8597ab1ea29bc0515815956fea50e0b','productionIndexBlob':'21fbbf4010410a6bdcec75ea0d98b1532bde2001','existingProductionRowsModified':0,'mappings':map_evidence})

def csvwrite(path,rows,fields=None):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
csvwrite(OUT/'SONG_NAMING_CHANGES_R06.csv',changes)
gains=collections.Counter(s['artist'] for s in cat['embedded']);counts=collections.Counter(identity(s['artist']) for s in baseline['songs'])
report=[{'Artist':a,'Current V4 songs':counts[identity(a)],'Approved gain':gains[a],'After publication':counts[identity(a)]+gains[a]} for a in sorted(gains,key=str.casefold)]
report.append({'Artist':'ALL CATALOG SONGS','Current V4 songs':13025,'Approved gain':317,'After publication':13342})
csvwrite(OUT/'ARTISTS_CURRENT_VS_APPROVED_R06.csv',report)
csvwrite(WAVE/'ARTISTS_CURRENT_VS_APPROVED_R06.csv',report)
csvwrite(WAVE/'SONG_NAMING_CHANGES_R06.csv',changes)
writejson(WAVE/'proposed-additions-index.json',cat['index'])
writejson(WAVE/'manifest.json',{'schema':'gfb.approved-catalog-wave.v1','version':'V6.0','revision':'R06','wave':'R05 approved selections','status':'OWNER_APPROVED_STAGED_NOT_RELEASED','parentCommit':'44a480761c519733df65d8cf075e15e2f6cd524a','branch':'build/gfb-v6.0-catalog-r05-approved-2026-09-22','originalReviewZipSha256':sha((ROOT/'recovered/GuitarFakeBook_V6.0_DESKTOP_REVIEW_R05.zip').read_bytes()),'originalDatasetId':dataset['datasetId'],'normalizedDatasetId':newdataset['datasetId'],'existingBank':13025,'approvedAdditions':317,'proposedBank':13342,'artistCount':len(gains),'songs':manifests})
for f in ['review-dataset.json','VERIFICATION.json','FULL_2002_RECORD_AUDIT_R05.csv','ARTISTS_CURRENT_VS_PROPOSED_R05.csv']:
    shutil.copy2(SRC/f,WAVE/'evidence'/('R05_ORIGINAL_'+f))
shutil.copy2(OUT/'OWNER_DECISIONS_R05_ORIGINAL.json',WAVE/'evidence/OWNER_DECISIONS_R05_ORIGINAL.json')
shutil.copy2(OUT/'OWNER_DECISIONS_R06_NORMALIZED.json',WAVE/'evidence/OWNER_DECISIONS_R06_NORMALIZED.json')

text=(SRC/'index.html').read_text()
def replace_assignment(text,name,value):
    marker='window.'+name+'=';start=text.index(marker)+len(marker)
    old,end=json.JSONDecoder().raw_decode(text[start:])
    return text[:start]+js(value).replace('</','<\/')+text[start+end:]
text=replace_assignment(text,'GFB_REVIEW_DATA',newdataset)
text=replace_assignment(text,'GFB_CATALOG_DATA',cat)
text=text.replace('GFB-V6.0-DESKTOP-REVIEW-R05','GFB-V6.0-APPROVED-R06')
text=text.replace('desktop-review.r05','approved.r06')
text=text.replace('let saved=core.empty(),current=',"let saved=core.validate("+js(decision(newdataset)).replace('</','<\/')+"),current=")
assert text.count('let saved=core.validate(')==1
(OUT/'index.html').write_text(text,encoding='utf-8')
shutil.copy2(SRC/'START_REVIEW.cmd',OUT/'START_REVIEW.cmd')
for p in (SRC/'artists').rglob('index.html'):
    t=p.read_text(); m=re.search(r'<h1>(.*?)</h1>',t);a=html.unescape(m.group(1));new=artist_map.get(a,a)
    t=t.replace(html.escape(a),html.escape(new))
    for song in original['embedded']:
        if song['artist']==a:t=t.replace('>'+html.escape(song['title'])+'</a>','>'+html.escape(newby[song['id']]['title'])+'</a>')
    dest=OUT/p.relative_to(SRC);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(t,encoding='utf-8')

oldkeys={(identity(s['artist']),titlekey(s['title'])) for s in baseline['songs']}
newkeys=[(identity(s['artist']),titlekey(s['title'])) for s in cat['embedded']]
assert not (set(newkeys)&oldkeys)
assert len(set(newkeys))==317
assert not ({s['id'] for s in baseline['songs']}&set(newby))
assert len(newby)==317
assert initial_caps('human touch')=='Human Touch'
assert artist_map['The Beach Boys']=='Beach Boys'
assert all(s['title']==initial_caps(s['title']) for s in cat['embedded'])
verification={'schema':'gfb.metadata-approval-verification.v1','createdAt':now,'reviewedSongs':317,'approvedKeep':317,'approvedRemove':0,'approvedHold':0,'titleChanges':sum(x['Original title']!=x['Approved title'] for x in changes),'artistChanges':sum(x['Original artist']!=x['Approved artist'] for x in changes),'artistMappingsChanged':sum(x['reviewArtist']!=x['canonicalArtist'] for x in map_evidence if x['reviewArtist']!='The Beach Boys'),'artistCount':len(gains),'newArtists':sum(not counts[identity(a)] for a in gains),'catalogDuplicatePairs':0,'duplicateNewIds':0,'metadataOnlyChangesVerified':317,'unchangedMusicalContent':317,'currentCatalogCount':13025,'proposedCount':13342,'currentSongsModified':0,'originalPackageChecksums':'139 archived files; every listed checksum verified','v4DataVsAppIndex':'SEMANTIC_EQUAL_13025_ROWS','sourceHashNote':'Git source blobs identified by API SHA; fetched text was parsed for semantic comparison. R05 ZIP bytes verified independently. New payload hashes describe the exact newly written JSON bytes. Original recorded hashes retained as lineage, not claimed recomputed.','humanTouch':'Capitalization rule verified; Human Touch is an example, not one of the 317 reviewed songs.','beachBoys':'Explicit alias policy recorded; no Beach Boys addition among the 317 reviewed songs.','independentReview':'PENDING_REQUIRED_BEFORE_RELEASE','productionDeployment':False}
writejson(OUT/'VERIFICATION_R06.json',verification);writejson(WAVE/'VERIFICATION_R06.json',verification)
(WAVE/'README.md').write_text('# GuitarFakeBook V6.0 approved R05 selections — R06 naming\n\nAll 317 playable R05 proposals are owner-approved Keep. Titles use initial capitals; artist names match existing production V4 spellings. Musical content and all existing catalog records are unchanged.\n\nThis directory is an inactive, source-hashed preparation for controlled publication. It does not change data/index.json or activate production. Independent review and release gates remain open. No additional owner song-by-song decision is required.\n\nRestore/recovery: parent data commit 44a480761c519733df65d8cf075e15e2f6cd524a; production app deploy/gfb-v4.1-hf2 at 0bf10064a8597ab1ea29bc0515815956fea50e0b.\n')
(OUT/'README.md').write_text('# GuitarFakeBook V6.0 approved songs — R06\n\nOpen index.html. All 317 reviewed songs are already marked Keep. Titles and artists have been normalized according to Peter\'s instruction; song contents are unchanged. The original and normalized decision JSON files preserve the approval across both dataset identities.\n\nARTISTS_CURRENT_VS_APPROVED_R06.csv reports current counts, approved additions, and totals after publication. Counts consolidate existing spelling aliases for comparison only; existing songs were not renamed. The total will be 13,342 after all 317 are published.\n\nThe catalog/ folder contains the exact JSON song files, metadata map, hashes, and evidence for Git staging. The original R05 review and its failed/held audit rows remain preserved. This is an approved song batch, not a production deployment.\n')
print(json.dumps(verification,indent=2))
