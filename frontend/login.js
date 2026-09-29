'use strict';
const $=id=>document.getElementById(id);
$('login-form').onsubmit=async e=>{e.preventDefault();$('login-submit').disabled=true;$('login-error').textContent='';try{const r=await fetch('/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tenant:$('tenant').value.trim(),user:$('account').value.trim(),password:$('password').value})});const result=await r.json();if(!r.ok)throw Error(result.detail||'登录失败');SupportSession.save(result);$('password').value='';location.assign(result.principal.roles.some(x=>['staff','admin'].includes(x))?'/desk':result.principal.roles.includes('finance')?'/admin':'/');}catch(e){$('login-error').textContent=e.message;}finally{$('login-submit').disabled=false;}};
document.querySelectorAll('[data-path]').forEach(b=>b.onclick=()=>{SupportSession.save(null);location.assign(b.dataset.path);});
fetch('/health').then(r=>r.json()).then(d=>$('demo-links').hidden=!d.demo).catch(()=>{});
