// Django API base
const API_BASE = 'http://127.0.0.1:8000/api';

// Local fallback (optional)
const USERS_KEY='bookshare_users'; const SESSION_KEY='bookshare_session';
function loadUsers(){ try{const u=JSON.parse(localStorage.getItem(USERS_KEY)); return Array.isArray(u)?u:[];}catch{return [];} }
function saveUsers(arr){ localStorage.setItem(USERS_KEY, JSON.stringify(arr)); }
function getSession(){ try{ return JSON.parse(localStorage.getItem(SESSION_KEY)) }catch{ return null } }
function setSession(s){ localStorage.setItem(SESSION_KEY, JSON.stringify(s)) }
function clearSession(){ localStorage.removeItem(SESSION_KEY) }

async function apiRegister(payload){
  const res = await fetch(`${API_BASE}/auth/register`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
  if(!res.ok){ throw new Error((await res.json()).error || 'Registration failed'); }
  return res.json();
}
async function apiLogin(payload){
  const res = await fetch(`${API_BASE}/auth/login`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
  if(!res.ok){ throw new Error((await res.json()).error || 'Login failed'); }
  return res.json();
}
async function apiMe(token){
  const res = await fetch(`${API_BASE}/auth/me`, { headers:{'Authorization':`Bearer ${token}`} });
  if(!res.ok){ throw new Error('Auth check failed'); }
  return res.json();
}

function ensureRole(role){
  const s=getSession();
  if(!s){ window.location.href = '../index.html'; return; }
  if(s.token){ apiMe(s.token).catch(()=>{ clearSession(); window.location.href='../index.html'; }); }
  if(s.user.role!==role){
    if(s.user.role==='student') window.location.href='../student/dashboard.html';
    if(s.user.role==='faculty') window.location.href='../faculty/dashboard.html';
    if(s.user.role==='admin')   window.location.href='../admin/dashboard.html';
  }
  const who=document.getElementById('whoami'); if(who) who.textContent = `${s.user.name} (${s.user.email})`;
  const chip=document.getElementById('roleChip'); if(chip) chip.textContent = `Role: ${s.user.role}`;
}
function logout(){ clearSession(); window.location.href = 'index.html'; }
function logoutUp(){ clearSession(); window.location.href = '../index.html'; }
function activateNav(id){ const a=document.querySelector(`[data-id="${id}"]`); if(a){ a.classList.add('active'); } }

document.addEventListener('DOMContentLoaded', ()=>{
  const loginForm = document.getElementById('loginForm');
  if(loginForm){
    loginForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const email=document.getElementById('email').value.trim();
      const password=document.getElementById('password').value.trim();
      const role=document.getElementById('role').value;
      const er=document.getElementById('loginError');
      try{
        const out = await apiLogin({email,password,role});
        setSession({ token: out.token, user: out.user, backend:true });
        const r = out.user.role;
        if(r==='student') location.href='student/dashboard.html';
        else if(r==='faculty') location.href='faculty/dashboard.html';
        else location.href='admin/dashboard.html';
      }catch(err){
        er.textContent = err.message || 'Login failed'; er.style.display='block';
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
      const er=document.getElementById('registerError');
      try{
        const out = await apiRegister({name,email,password,role,year,branch});
        setSession({ token: out.token, user: out.user, backend:true });
        if(role==='student') location.href='student/dashboard.html'; else if(role==='faculty') location.href='faculty/dashboard.html'; else location.href='admin/dashboard.html';
      }catch(err){
        er.textContent = err.message || 'Registration failed'; er.style.display='block';
      }
    });
  }
});


// ===== Simple helpers for feature pages =====
function authHeader(){
  const s = getSession(); return s && s.token ? {'Authorization':`Bearer ${s.token}`} : {};
}

async function apiListAds(){
  const res = await fetch(`${API_BASE}/ads/`, { headers: authHeader() });
  return res.json();
}
async function apiMyAds(){
  const res = await fetch(`${API_BASE}/ads/mine/`, { headers: authHeader() });
  return res.json();
}
async function apiCreateAd(payload){
  const res = await fetch(`${API_BASE}/ads/`, { method:'POST', headers:{'Content-Type':'application/json', ...authHeader()}, body:JSON.stringify(payload) });
  if(!res.ok){ throw new Error('Failed to create ad'); } return res.json();
}
async function apiListMaterials(){
  const res = await fetch(`${API_BASE}/materials/`, { headers: authHeader() });
  return res.json();
}
