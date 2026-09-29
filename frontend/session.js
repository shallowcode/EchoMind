'use strict';
window.SupportSession = (() => {
  const key='supportflow.account';
  const read=()=>{try{return JSON.parse(sessionStorage.getItem(key)||'null');}catch{return null;}};
  function save(value){try{if(value)sessionStorage.setItem(key,JSON.stringify(value));else sessionStorage.removeItem(key);}catch{}}
  async function establish(audience){
    const stored=read();
    if(stored){const r=await fetch('/auth/me',{headers:{Authorization:'Bearer '+stored.token}});if(r.ok)return {...stored,principal:await r.json()};save(null);location.assign('/login');throw Error('登录已过期');}
    const r=await fetch('/auth/demo-'+audience,{method:'POST',headers:{'X-SupportFlow-Demo':audience}});
    if(!r.ok){location.assign('/login');throw Error('请登录');}
    const data=await r.json();return {...data,demo:true};
  }
  async function logout(token){try{await fetch('/auth/logout',{method:'POST',headers:{Authorization:'Bearer '+token}});}finally{save(null);location.assign('/login');}}
  // Reconnect using the last durable event ID; credentials never enter URLs.
  function subscribe(getToken,onChange,onExpired=()=>{},onConnection=()=>{}){
    const controller=new AbortController();let cursor=0;
    (async()=>{while(!controller.signal.aborted){try{
      const response=await fetch('/events?after='+cursor,{headers:{Authorization:'Bearer '+getToken()},signal:controller.signal});
      if(response.status===401){await onExpired();throw Error('session expired');}if(!response.ok)throw Error('stream unavailable');onConnection(true);
      const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='';
      while(true){const {value,done}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});let end;
        while((end=buffer.indexOf('\n\n'))!==-1){const event=buffer.slice(0,end);buffer=buffer.slice(end+2);const line=event.split('\n').find(l=>l.startsWith('data: '));if(line){const data=JSON.parse(line.slice(6));cursor=data.id;onChange(data);}}}
    }catch(error){if(controller.signal.aborted)break;onConnection(false);}await new Promise(resolve=>{const finish=()=>{clearTimeout(timer);controller.signal.removeEventListener('abort',finish);resolve();};const timer=setTimeout(finish,2000);controller.signal.addEventListener('abort',finish,{once:true});});}})();
    return ()=>controller.abort();
  }
  return {establish,save,read,logout,subscribe};
})();
