
function pickCover(title){
  title = (title||'').toLowerCase();
  if(title.includes('dbms')) return '../assets/images/covers/dbms.svg';
  if(title.includes('operating')||title.includes('os')) return '../assets/images/covers/os.svg';
  if(title.includes('network')) return '../assets/images/covers/cn.svg';
  return '../assets/images/covers/default.svg';
}

function enhanceBrowse(){
  const grid = document.querySelector('.grid.grid-3');
  if(!grid) return;
  const cards = grid.querySelectorAll('.card');
  cards.forEach(card => {
    if(card.classList.contains('h-card')) return;
    const titleEl = card.querySelector('b');
    const title = titleEl ? titleEl.textContent.trim() : '';
    const cover = pickCover(title);
    card.classList.add('h-card');
    card.innerHTML = `<img class="cover" src="${cover}" alt="cover"><div>${card.innerHTML}</div>`;
  });
}

function enhanceMyAds(){
  const tbody = document.querySelector('#myAdsTbody') || document.querySelector('tbody');
  if(!tbody) return;
  const headRow = document.querySelector('thead tr');
  if(headRow && !headRow.dataset.coverAdded){
    const th = document.createElement('th'); th.textContent = 'Cover';
    headRow.insertBefore(th, headRow.firstElementChild);
    headRow.dataset.coverAdded = '1';
  }
  tbody.querySelectorAll('tr').forEach(tr => {
    if(tr.dataset.coverAdded) return;
    const tds = tr.querySelectorAll('td');
    let title = '';
    if(tds.length >= 2){
      // Try to guess title column
      for(const td of tds){
        if(td.textContent && td.textContent.length > 0 && !td.textContent.startsWith('₹')){
          title = td.textContent.trim(); break;
        }
      }
    }
    const coverTd = document.createElement('td');
    coverTd.innerHTML = `<img class="cover" src="${pickCover(title)}" alt="cover">`;
    tr.insertBefore(coverTd, tr.firstElementChild);
    tr.dataset.coverAdded = '1';
  });
}

window.addEventListener('load', ()=>{
  setTimeout(enhanceBrowse, 200);
  setTimeout(enhanceMyAds, 400);
});
