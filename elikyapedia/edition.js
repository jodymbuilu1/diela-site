/* The catalogue search stays in the visitor's browser. */
(() => {
  const input = document.querySelector('#article-search');
  if (input) {
    const cards = [...document.querySelectorAll('.article-card')];
    const count = document.querySelector('[data-result-count]');
    const empty = document.querySelector('.no-results');
    const clear = document.querySelector('[data-clear]');
    const normalize = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const filter = () => {
      const words = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
      let found = 0;
      cards.forEach(card => {
        const match = words.every(word => normalize(card.dataset.search).includes(word));
        card.hidden = !match;
        found += Number(match);
      });
      count.textContent = `${found} article${found === 1 ? '' : 's'}`;
      count.setAttribute('aria-live', 'polite');
      empty.hidden = found !== 0;
      clear.hidden = input.value.length === 0;
    };
    input.addEventListener('input', filter);
    clear.addEventListener('click', () => { input.value = ''; filter(); input.focus(); });
  }
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
})();
