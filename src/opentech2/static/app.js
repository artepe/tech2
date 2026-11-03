(() => {
  'use strict';
  const token = document.querySelector('meta[name="app-token"]').content;
  const $ = id => document.getElementById(id);
  const names = {overview:'Ajoneuvon yleiskuva',live:'Mittausarvot',faults:'Vikakoodit',ecu:'ECU-tunnisteet',cards:'Ohjelmistokortit',security:'Turvapääsy'};
  let catalog;
  const asText = (el, text) => { el.textContent = text; };
  const make = (tag, cls, text) => { const el=document.createElement(tag); if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el; };
  async function api(route, data) {
    const opts = data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json','X-Tech2-Token':token},body:JSON.stringify(data)};
    const res = await fetch(route, opts);
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || `HTTP ${res.status}`);
    return body;
  }
  function report(err) { const b=$('error-banner');b.textContent=err.message||String(err);b.classList.remove('hidden'); }
  function resetError(){ $('error-banner').classList.add('hidden'); }
  function showPanel(id) {
    document.querySelectorAll('.panel').forEach(el=>el.classList.toggle('active',el.id===id));
    document.querySelectorAll('.nav').forEach(el=>el.classList.toggle('active',el.dataset.panel===id));
    asText($('page-title'),names[id]);
    if(id==='live') fetchLive();
    if(id==='faults') fetchDtcs();
    if(id==='cards') fetchCards();
    if(id==='security') fetchSecurity();
  }
  async function status(){
    const state=await api('/api/status');
    $('demo-banner').classList.toggle('hidden',!state.demo);
    const chip=$('connection-badge'); chip.textContent=state.demo?'DEMO':state.connected?'Yhdistetty':'Ei yhteyttä';chip.classList.toggle('connected',state.connected&&!state.demo);
    asText($('status-adapter'),state.adapter||'Ei yhteyttä');
    asText($('status-vehicle'),[state.brand,state.model].filter(Boolean).join(' '));
    $('brand').value=state.brand; $('model').value=state.model;
    return state;
  }
  async function fetchLive(){
    resetError();const grid=$('sensor-grid');grid.replaceChildren(make('div','empty','Haetaan arvoja…'));
    try { const reply=await api('/api/live');grid.replaceChildren();
      Object.values(reply.data).forEach(data=>{
        const el=make('article','metric'+(data.value===null?' error-value':''));
        el.append(make('div','name',data.label));
        const value=make('strong');value.textContent=data.value===null?'Ei saatavilla':String(data.value)+' ';
        if(data.value!==null)value.append(make('small','',data.unit));
        el.append(value);if(data.error)el.append(make('div','hint',data.error));grid.append(el);
      });
    }catch(e){grid.replaceChildren(make('div','empty','Lukeminen ei onnistunut'));report(e);}
  }
  async function fetchDtcs(){
    resetError(); const list=$('dtc-list');list.replaceChildren(make('div','empty','Haetaan vikakoodeja…'));
    try{const result=await api('/api/dtcs');list.replaceChildren();
      if(!result.data.length){list.append(make('span','empty','Geneerisiä vikakoodeja ei löytynyt.'));return;}
      result.data.forEach(code=>list.append(make('span','dtc',code)));
    }catch(e){list.replaceChildren(make('span','empty','Vikakoodeja ei voitu lukea.'));report(e);}
  }
  function showIdResults(container, items){
    container.replaceChildren();
    items.forEach(item=>{
      const el=make('div','identity-row');
      el.append(make('span','identity-label',item.name||item.did));
      el.append(make('strong','identity-value',item.status==='ok'?item.value:(item.error||'Ei saatavilla')));
      el.append(make('small','identity-kind',item.did||''));
      container.append(el);
    });
  }
  async function fetchObdVin(){
    resetError();
    $('obd-vin-result').replaceChildren(make('div','hint','Luetaan...'));
    try{
      const result=await api('/api/vehicle-identification');
      const d=result.data;
      showIdResults($('obd-vin-result'),[{name:'Ajoneuvon VIN',value:d.vin,did:d.source,status:'ok'}]);
      if(result.demo)$('obd-vin-result').prepend(make('div','demo-marker','DEMO — EI OIKEA VIN'));
    }catch(e){$('obd-vin-result').replaceChildren();report(e);}
  }
  async function fetchUds(isDemo){
    resetError();
    const results=$('uds-list');results.replaceChildren(make('div','hint','Odotetaan ECU-vastausta...'));
    try{
      const payload={demo:isDemo,dids:['F190','F187','F188']};
      if(!isDemo){
        payload.interface=$('can-interface').value.trim();
        payload.txid=$('can-txid').value.trim();
        payload.rxid=$('can-rxid').value.trim();
      }
      const reply=await api('/api/ecu/uds',payload);
      showIdResults(results,reply.data);
      if(reply.demo)results.prepend(make('div','demo-marker','DEMO — SIMULOIDUT VASTAUKSET'));
    }catch(e){results.replaceChildren();report(e);}
  }
  async function fetchCards(){
    const grid=$('card-grid');grid.replaceChildren();
    catalog.card_families.forEach(c=>{
      const el=make('article','card-item');el.append(make('strong','',c.name));el.append(make('small','',c.makes.join(' · ')));el.append(make('span','','VAIN METATIEDOT'));grid.append(el);
    });
    try {const cards=await api('/api/cards');asText($('registered-cards'),cards.length?`Rekisteröityjä tiedostotiivisteitä: ${cards.length}`:'Ei vielä rekisteröityjä korttitiedostoja.');}catch(e){report(e);}
  }
  async function fetchSecurity(){
    try{const items=await api('/api/security');const grid=$('protected-actions');grid.replaceChildren();
      items.forEach(item=>{const el=make('div','security-item');el.append(make('strong','',item.feature));el.append(make('span','','LUKITTU – VALMISTAJAN TOTEUTUS PUUTTUU'));grid.append(el);});
    }catch(e){report(e);}
  }
  async function changeVehicle(){resetError();try{await api('/api/select',{brand:$('brand').value,model:$('model').value});await status();}catch(e){report(e);}}
  async function connect(){resetError();try{await api('/api/connect',{brand:$('brand').value,model:$('model').value,port:$('port').value.trim(),baud:Number($('baud').value)});await status();}catch(e){report(e);}}
  async function disconnect(){resetError();try{await api('/api/disconnect',{});await status();}catch(e){report(e);}}
  async function init(){try{
    catalog=await api('/api/catalog');
    catalog.makes.forEach(m=>{const option=make('option','',m.name);option.value=m.name;$('brand').append(option);});
    await status();
    document.querySelectorAll('.nav').forEach(b=>b.addEventListener('click',()=>showPanel(b.dataset.panel)));
    $('save-vehicle').addEventListener('click',changeVehicle);
    $('connect').addEventListener('click',connect);
    $('disconnect').addEventListener('click',disconnect);
    $('refresh-live').addEventListener('click',fetchLive);
    $('refresh-dtcs').addEventListener('click',fetchDtcs);
    $('read-obd-vin').addEventListener('click',fetchObdVin);
    $('demo-uds').addEventListener('click',()=>fetchUds(true));
    $('read-uds').addEventListener('click',()=>fetchUds(false));
  }catch(e){report(e);}}
  init();
})();
