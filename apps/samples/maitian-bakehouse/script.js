  // current year
  document.getElementById('year').textContent = new Date().getFullYear();

  // mobile nav
  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');
  navToggle.addEventListener('click', function(){
    var open = navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  navLinks.querySelectorAll('a').forEach(function(a){
    a.addEventListener('click', function(){
      navLinks.classList.remove('open');
      navToggle.setAttribute('aria-expanded','false');
    });
  });

  // scroll reveal
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.reveal').forEach(function(el){ io.observe(el); });

  // gentle parallax on hero photo
  var frame = document.querySelector('.photo-frame');
  if(frame && !window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    window.addEventListener('scroll', function(){
      var y = Math.min(window.scrollY, 600);
      frame.style.transform = 'rotate(-1.2deg) translateY(' + (y * -0.05) + 'px)';
    }, { passive: true });
  }
