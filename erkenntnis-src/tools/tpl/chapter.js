
(function(){
  var b=document.body;
  function store(k,v){ try{localStorage.setItem(k,v);}catch(e){} }
  function load(k){ try{return localStorage.getItem(k);}catch(e){return null;} }
  function setV(v){ b.classList.remove('only-de','only-jp'); if(v!=='both') b.classList.add(v);
    document.querySelectorAll('[data-v]').forEach(function(x){x.setAttribute('aria-pressed',x.dataset.v===v);}); store('mach-ei-view',v); }
  function setN(n){ b.classList.toggle('no-notes',n==='no-notes');
    document.querySelectorAll('[data-n]').forEach(function(x){x.setAttribute('aria-pressed',x.dataset.n===n);}); store('mach-ei-notes',n); }
  document.querySelectorAll('[data-v]').forEach(function(x){x.addEventListener('click',function(){setV(x.dataset.v);});});
  document.querySelectorAll('[data-n]').forEach(function(x){x.addEventListener('click',function(){setN(x.dataset.n);});});
  setV(load('mach-ei-view')||'both'); setN(load('mach-ei-notes')||'show');
})();
