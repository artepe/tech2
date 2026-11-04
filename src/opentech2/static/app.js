(() => {
  'use strict';
  const token = document.querySelector('meta[name="app-token"]').content;
  const $ = id => document.getElementById(id);
  const names = {overview:'Ajoneuvon yleiskuva',chrysler:'Chrysler 300 -mallit',live:'Mittausarvot',faults:'Vikakoodit',ecu:'ECU-tunnisteet',cards:'Ohjelmistokortit',security:'Turvapääsy'};
  let catalog;
  let chryslerProfile = null;
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
    if(id==='chrysler') loadChryslerProfile();
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

  function renderChrysler(data){
    const info=$('chrysler-profile-info');
    const variants=$('chrysler-variant');
    info.replaceChildren();
    variants.replaceChildren();
    const p=data.selected;
    if(!p){
      chryslerProfile=null;
      $('chrysler-apply').disabled=true;
      const historical=data.year_query!==null && data.year_query>=1955 && data.year_query<=1965;
      info.append(make('p','',historical?'Historiallinen Chrysler 300 -mallisarja ei käytä OBD-II:ta.':'Tälle vuosimallille ei ole Chrysler 300 -profiilia. Tuotanto päättyi vuonna 2023.'));
      return;
    }
    chryslerProfile=p;
    $('chrysler-apply').disabled=false;
    info.append(make('h2','',p.title));
    info.append(make('div','hint','Vuosimallit '+p.start_year+'–'+p.end_year));
    info.append(make('p','',p.architecture));
    const nets=make('div','chrysler-networks');
    p.networks.forEach(n=>nets.append(make('div','chrysler-network',n)));
    info.append(nets);
    info.append(make('p','',p.transport_notes));
    info.append(make('p','',p.access_notes));
    info.append(make('p','chrysler-warning','OEM-luku ja ECU-koodaus eivät ole käytössä. Oikean Chrysler-auton yhteyttä ei ole testattu.'));
    p.variants.forEach(name=>{const option=make('option','',name);option.value=name;variants.append(option);});
  }
  async function loadChryslerProfile(){
    resetError();
    const year=Number($('chrysler-year').value);
    if(!Number.isInteger(year)||year<1955||year>2023){report(new Error('Anna mallivuosi 1955–2023'));return;}
    try{
      const data=await api('/api/chrysler-300?year='+year);
      renderChrysler(data);
      const grid=$('chrysler-generations');grid.replaceChildren();
      data.profiles.forEach(p=>{
        const el=make('article','card-item');
        el.append(make('strong','',p.title));
        el.append(make('small','',p.start_year+'–'+p.end_year));
        el.append(make('span','','OBD-II TESTAAMATON · OEM EI TOTEUTETTU'));
        grid.append(el);
      });
    }catch(e){report(e);}
  }
  async function applyChryslerProfile(){
    resetError();
    if(!chryslerProfile){report(new Error('Valitse profiili ensin'));return;}
    const year=Number($('chrysler-year').value);
    const variant=$('chrysler-variant').value;
    if(year<chryslerProfile.start_year||year>chryslerProfile.end_year||!chryslerProfile.variants.includes(variant)){
      report(new Error('Profiili ei vastaa vuosimallia'));return;
    }
    try{
      await api('/api/select',{brand:'Chrysler',model:variant+' '+year});
      await status();
      showPanel('overview');
    }catch(e){report(e);}
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
    $('chrysler-profile-load').addEventListener('click',loadChryslerProfile);
    $('chrysler-apply').addEventListener('click',applyChryslerProfile);
  }catch(e){report(e);}}
  init();
})();
