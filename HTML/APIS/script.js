const initialData = ['Bones', 'Castle', 'The Mentalist'];
let favorites = JSON.parse(localStorage.getItem('flix_favs')) || initialData;

const grid = document.getElementById('series-grid');
const searchInput = document.getElementById('search-input');
const resultsBox = document.getElementById('search-results');

// Carga ultra-rápida en paralelo
async function init() {
    grid.innerHTML = '';
    const promises = favorites.map(name => fetch(`https://api.tvmaze.com/singlesearch/shows?q=${name}`).then(r => r.json()));
    const data = await Promise.all(promises);
    data.forEach(serie => renderCard(serie));
}

// Buscador Predictivo
searchInput.addEventListener('input', async (e) => {
    const query = e.target.value;
    if (query.length < 2) { resultsBox.classList.add('hidden'); return; }

    const res = await fetch(`https://api.tvmaze.com/search/shows?q=${query}`);
    const items = await res.json();
    
    resultsBox.innerHTML = '';
    resultsBox.classList.remove('hidden');

    items.slice(0, 6).forEach(({show}) => {
        const div = document.createElement('div');
        div.className = 'result-item';
        div.innerHTML = `
            <img src="${show.image?.medium || 'https://via.placeholder.com/45x60/111/333'}">
            <div>
                <h4 class="text-white">${show.name}</h4>
                <p class="text-xs text-gray-500">${show.genres[0] || 'Serie'}</p>
            </div>
        `;
        div.onclick = () => {
            if (!favorites.includes(show.name)) {
                favorites.push(show.name);
                localStorage.setItem('flix_favs', JSON.stringify(favorites));
                renderCard(show);
            }
            resultsBox.classList.add('hidden');
            searchInput.value = '';
        };
        resultsBox.appendChild(div);
    });
});

function renderCard(serie) {
    const card = document.createElement('div');
    card.className = 'serie-card';
    card.innerHTML = `<img src="${serie.image?.medium || ''}" alt="${serie.name}">`;
    card.onclick = () => openModal(serie);
    grid.appendChild(card);
}

async function openModal(serie) {
    const modal = document.getElementById('modal');
    document.getElementById('modal-title').innerText = serie.name;
    document.getElementById('modal-img').src = serie.image?.original || '';
    document.getElementById('modal-rating').innerText = `★ ${serie.rating.average || '8.2'}`;
    document.getElementById('modal-year').innerText = `${serie.premiered?.split('-')[0] || '2000'} • ${serie.genres.join(', ')}`;
    
    // Botón de Video YouTube
    document.getElementById('btn-trailer').href = `https://www.youtube.com/results?search_query=${encodeURIComponent(serie.name)}+trailer+castellano`;

    // TRADUCCIÓN A ESPAÑOL
    const summaryBox = document.getElementById('modal-summary');
    summaryBox.innerText = "Traduciendo sinopsis al castellano...";
    const cleanText = serie.summary.replace(/<[^>]*>?/gm, '');
    
    try {
        const res = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(cleanText)}&langpair=en|es`);
        const data = await res.json();
        summaryBox.innerText = data.responseData.translatedText;
    } catch {
        summaryBox.innerHTML = serie.summary;
    }

    // RESEÑAS ALEATORIAS
    const reviewsBox = document.getElementById('reviews-container');
    reviewsBox.innerHTML = '';
    const userRes = await fetch('https://randomuser.me/api/?results=3');
    const userData = await userRes.json();
    
    const frases = ["Obra maestra absoluta.", "Personajes inolvidables.", "La he visto 3 veces.", "Guion brillante."];
    
    userData.results.forEach(user => {
        reviewsBox.innerHTML += `
            <div class="review-item">
                <img src="${user.picture.thumbnail}" class="review-avatar">
                <div>
                    <p class="text-sm font-bold">${user.name.first} ${user.name.last}</p>
                    <p class="text-xs text-gray-400 mt-1">"${frases[Math.floor(Math.random()*frases.length)]}"</p>
                </div>
            </div>`;
    });

    modal.classList.remove('hidden');
}

function closeModal() { document.getElementById('modal').classList.add('hidden'); }
function clearLibrary() { localStorage.clear(); location.reload(); }

document.addEventListener('click', (e) => { if (!e.target.closest('.search-box')) resultsBox.classList.add('hidden'); });

init();