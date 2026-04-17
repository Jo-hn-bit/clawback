// Landing page enhancements - kept lean

// Subtle nav background opacity on scroll
window.addEventListener('scroll', () => {
  const nav = document.querySelector('.nav');
  if (window.scrollY > 20) {
    nav.style.background = 'rgba(10, 10, 15, 0.85)';
  } else {
    nav.style.background = 'rgba(10, 10, 15, 0.7)';
  }
});

// Animate elements on scroll into view
const observerOptions = { threshold: 0.15, rootMargin: '0px 0px -50px 0px' };
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.step, .science-card, .stat').forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = `opacity 0.6s ease ${i * 0.08}s, transform 0.6s ease ${i * 0.08}s`;
  observer.observe(el);
});
