import '../../shared/site.css';

document.querySelector('[data-tc-menu]')?.addEventListener('click', () => {
  document.querySelector('.tc-site-bar')?.classList.toggle('is-open');
});
