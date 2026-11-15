(() => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  if (toggle && nav) toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  const slider = document.querySelector('[data-slider]');
  if (!slider) return;
  const slides = [...slider.querySelectorAll('.slide')];
  const dots = [...slider.querySelectorAll('.dot')];
  const status = slider.querySelector('[data-slide-status]');
  let current = 0;
  function show(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === current);
      slide.setAttribute('aria-hidden', String(i !== current));
    });
    dots.forEach((dot, i) => {
      dot.setAttribute('aria-current', String(i === current));
      dot.setAttribute('aria-label', `${i + 1}번 이미지 보기`);
    });
    if (status) status.textContent = `${current + 1} / ${slides.length}`;
  }
  slider.querySelector('[data-prev]')?.addEventListener('click', () => show(current - 1));
  slider.querySelector('[data-next]')?.addEventListener('click', () => show(current + 1));
  dots.forEach((dot, i) => dot.addEventListener('click', () => show(i)));
  show(0);
})();
