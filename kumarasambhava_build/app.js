(function(){
  var root=document.documentElement;
  function load(k,d){try{return localStorage.getItem(k)||d}catch(e){return d}}
  function save(k,v){try{localStorage.setItem(k,v)}catch(e){}}
  function setScript(v){
    root.setAttribute('data-script',v);
    document.querySelectorAll('[data-set-script]').forEach(function(b){
      b.setAttribute('aria-pressed',String(b.getAttribute('data-set-script')===v));});
    save('ks-script',v);
  }
  function setNotes(v){
    root.setAttribute('data-notes',v);
    var b=document.querySelector('[data-toggle-notes]');
    if(b){b.setAttribute('aria-pressed',String(v==='on'));b.textContent=v==='on'?'注 表示':'注 非表示';}
    save('ks-notes',v);
  }
  document.querySelectorAll('[data-set-script]').forEach(function(b){
    b.addEventListener('click',function(){setScript(b.getAttribute('data-set-script'));});});
  var nb=document.querySelector('[data-toggle-notes]');
  if(nb)nb.addEventListener('click',function(){setNotes(root.getAttribute('data-notes')==='on'?'off':'on');});
  var s=load('ks-script','dev'); if(['dev','iast','both'].indexOf(s)<0)s='dev';
  setScript(s); setNotes(load('ks-notes','on')==='off'?'off':'on');
})();
