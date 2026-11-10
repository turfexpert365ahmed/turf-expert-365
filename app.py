import os
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE = 'https://online.turfinfo.api.pmu.fr/rest/client/62/programme'
HEADERS = {'User-Agent':'Mozilla/5.0 TURF-EXPERT-365/1.0','Accept':'application/json','Origin':'https://www.pmu.fr'}

def pmu(path):
    response = requests.get(BASE + path, headers=HEADERS, timeout=12)
    response.raise_for_status()
    return response.json()

def today():
    return datetime.now(ZoneInfo('Europe/Paris')).strftime('%d%m%Y')

def date_value(raw):
    if not raw: return today()
    return datetime.strptime(raw,'%Y-%m-%d').strftime('%d%m%Y')

def number(x, default=0):
    try: return float(x)
    except (TypeError,ValueError): return default

def analyze(horses):
    results=[]
    for h in horses:
        if h.get('nonPartant'): continue
        # Heuristic, not an AI prediction: performance indicators when available.
        score=0
        reasons=[]
        musique=str(h.get('musique') or h.get('musiqueCheval') or '')
        recent=[int(c) for c in musique[:16] if c.isdigit() and c!='0'][:5]
        if recent:
            form=sum(max(0,11-n) for n in recent)/len(recent)
            score+=form*3
            reasons.append('Forme récente : '+musique[:24])
        gains=number(h.get('gainCarriere') or h.get('gainsCarriere'))
        if gains:
            import math
            score+=min(12,math.log10(max(1,gains))*2)
            reasons.append('Gains en carrière disponibles')
        if h.get('driver') or h.get('jockey'):
            reasons.append('Jockey/driver indiqué')
        results.append({'numero':h.get('numPmu') or h.get('numero'), 'nom':h.get('nom') or 'Cheval', 'score':round(score,1), 'raisons':reasons or ['Données insuffisantes pour évaluer ce cheval'], 'musique':musique, 'jockey':h.get('jockey') or h.get('driver') or '', 'entraineur':h.get('entraineur') or ''})
    results.sort(key=lambda h:h['score'],reverse=True)
    return results

@app.get('/')
def home(): return render_template('index.html')

@app.get('/api/reunions')
def reunions():
    try:
        d=date_value(request.args.get('date'))
        data=pmu('/'+d)
        items=data.get('programme',{}).get('reunions',[])
        return jsonify({'date':d,'reunions':[{'numero':r.get('numOfficiel') or r.get('numReunion'),'hippodrome':(r.get('hippodrome') or {}).get('libelleCourt') or (r.get('hippodrome') or {}).get('libelleLong') or 'Hippodrome', 'discipline':r.get('discipline')} for r in items]})
    except Exception as e:
        app.logger.warning('PMU reunions: %s',e)
        return jsonify({'error':'Les données des réunions ne sont pas accessibles actuellement depuis le serveur. Aucun programme inventé.'}),503

@app.get('/api/courses')
def courses():
    try:
        d=date_value(request.args.get('date'))
        r=int(request.args['reunion'])
        data=pmu(f'/{d}/R{r}')
        return jsonify({'courses':[{'numero':c.get('numOrdre'),'nom':c.get('libelle') or 'Course', 'distance':c.get('distance'),'discipline':c.get('discipline')} for c in data.get('courses',[])]})
    except Exception as e:
        app.logger.warning('PMU courses: %s',e)
        return jsonify({'error':'Courses indisponibles pour cette réunion.'}),503

@app.get('/api/analyse')
def analyse():
    try:
        d=date_value(request.args.get('date'))
        r=int(request.args['reunion']); c=int(request.args['course'])
        data=pmu(f'/{d}/R{r}/C{c}/participants')
        horses=data.get('participants',[]) if isinstance(data,dict) else data
        return jsonify({'classement':analyze(horses),'avertissement':'Classement indicatif fondé sur les seules données disponibles. Ce n’est pas une garantie de gain. Pedigree, terrain et cotes non vérifiés ne sont pas pris en compte.'})
    except Exception as e:
        app.logger.warning('PMU participants: %s',e)
        return jsonify({'error':'Partants indisponibles. Aucun pronostic inventé.'}),503

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','10000')))
