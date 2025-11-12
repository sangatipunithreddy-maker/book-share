function getSession(){ try{ return JSON.parse(localStorage.getItem('bookshare_session')) }catch{ return null } }
async function guard(){
  const s = getSession();
  if(!s || !s.tokens){ window.location.href = '/frontend/index.html'; return; }
  // set user name if element exists
  const nameEl = document.getElementById('userName');
  if(nameEl && s.user){ nameEl.textContent = s.user.first_name || s.user.username || s.user.email; }
}
document.addEventListener('DOMContentLoaded', guard);
