const API_BASE = 'http://127.0.0.1:8000/api';
const SESSION_KEY='bookshare_session';

function getSession(){ try{ return JSON.parse(localStorage.getItem(SESSION_KEY)) }catch{ return null } }
function setSession(s){ localStorage.setItem(SESSION_KEY, JSON.stringify(s)) }
function clearSession(){ localStorage.removeItem(SESSION_KEY) }

function authHeader(){
  const s = getSession();
  return s && s.tokens && s.tokens.access ? { 'Authorization': `Bearer ${s.tokens.access}` } : {};
}

async function apiRegister(payload){
  const res = await fetch(`${API_BASE}/auth/register`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
  const data = await res.json();
  if(!res.ok) throw new Error(data.error || JSON.stringify(data.errors) || 'Registration failed');
  return data;
}

async function apiLogin(payload){
  const res = await fetch(`${API_BASE}/auth/login`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
  const data = await res.json();
  if(!res.ok) throw new Error(data.error || 'Login failed');
  return data;
}

async function apiMe(){
  const res = await fetch(`${API_BASE}/auth/me`, { headers: { ...authHeader() }});
  if(!res.ok) throw new Error('Auth required');
  return res.json();
}

function goDashboard(role){
  if(role === 'faculty') window.location.href = '/frontend/faculty/dashboard.html';
  else if(role === 'admin') window.location.href = '/frontend/admin/dashboard.html';
  else window.location.href = '/frontend/student/dashboard.html';
}

// Wire login form on index.html
document.addEventListener('DOMContentLoaded', ()=>{
  const loginForm = document.getElementById('loginForm');
  if(loginForm){
    loginForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value.trim();
      const role = document.getElementById('role') ? document.getElementById('role').value : null;
      const err = document.getElementById('loginError');
      try{
        const out = await apiLogin({username: email, password});
        // Optional: enforce role match if user selects role
        if(role && out.user.role !== role){
          throw new Error(`This account is ${out.user.role}, not ${role}`);
        }
        setSession(out);
        goDashboard(out.user.role);
      }catch(ex){
        if(err){ err.textContent = ex.message; err.style.display='block'; }
        console.error(ex);
      }
    });
  }

  const regForm = document.getElementById('registerForm');
  if(regForm){
    regForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const name=document.getElementById('r_name').value.trim();
      const email=document.getElementById('r_email').value.trim();
      const password=document.getElementById('r_password').value.trim();
      const role=document.getElementById('r_role').value;
      const year=document.getElementById('r_year').value.trim();
      const branch=document.getElementById('r_branch').value.trim();
      const err=document.getElementById('registerError');
      try{
        const payload = { username: email, email, password, role, first_name: name, year, branch };
        const out = await apiRegister(payload);
        setSession(out);
        goDashboard(out.user.role);
      }catch(ex){
        if(err){ err.textContent = ex.message; err.style.display='block'; }
        console.error(ex);
      }
    });
  }

  // Logout buttons
  const logoutEls = document.querySelectorAll('[data-logout]');
  logoutEls.forEach(el=>{
    el.addEventListener('click', ()=>{
      clearSession();
      window.location.href = '/frontend/index.html';
    });
  });
});
