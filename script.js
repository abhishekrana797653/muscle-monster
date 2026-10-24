/**
 * MUSCLE MONSTER GYM — SCRIPT.JS
 * Implements:
 * 1. Page-load and scroll-triggered graceful slide-in animations (left, right, bottom).
 * 2. Dramatic scroll-triggered number counter animations.
 * 3. Mobile navigation menu toggle.
 * 4. Interactive gallery lightbox.
 * 5. Direct WhatsApp pass claim integration.
 */

document.addEventListener('DOMContentLoaded', () => {

  /* --------------------------------------------------------------------------
     1. SCROLL-TRIGGERED & PAGE-LOAD SLIDE-IN ANIMATIONS
     -------------------------------------------------------------------------- */
  const animElements = document.querySelectorAll('.anim-fade-up, .anim-slide-left, .anim-slide-right, .anim-fade');

  if (animElements.length > 0) {
    const observerOptions = {
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px'
    };

    const animObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated-in');
          observer.unobserve(entry.target); // Animate once
        }
      });
    }, observerOptions);

    animElements.forEach(el => animObserver.observe(el));

    // Page-Load Hero Trigger: Trigger initial above-the-fold elements smoothly
    setTimeout(() => {
      const heroElements = document.querySelectorAll('.hero-section .anim-fade-up, .hero-section .anim-slide-left, .hero-section .anim-slide-right');
      heroElements.forEach(el => el.classList.add('animated-in'));
    }, 60);
  }

  /* --------------------------------------------------------------------------
     2. DRAMATIC SCROLL-TRIGGERED COUNTER ANIMATION
     -------------------------------------------------------------------------- */
  const counters = document.querySelectorAll('.counter-animate');
  
  if (counters.length > 0) {
    const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

    const animateCounter = (counterElement) => {
      const target = parseFloat(counterElement.getAttribute('data-target')) || 0;
      const suffix = counterElement.getAttribute('data-suffix') || '';
      const prefix = counterElement.getAttribute('data-prefix') || '';
      const duration = parseInt(counterElement.getAttribute('data-duration'), 10) || 2000;
      let startTime = null;

      const step = (timestamp) => {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        const easedProgress = easeOutCubic(progress);
        const currentVal = Math.floor(easedProgress * target);

        counterElement.textContent = `${prefix}${currentVal}${suffix}`;

        if (progress < 1) {
          window.requestAnimationFrame(step);
        } else {
          counterElement.textContent = `${prefix}${target}${suffix}`;
        }
      };

      window.requestAnimationFrame(step);
    };

    const counterObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.3,
      rootMargin: '0px 0px -30px 0px'
    });

    counters.forEach(counter => {
      counter.textContent = '0';
      counterObserver.observe(counter);
    });
  }

  /* --------------------------------------------------------------------------
     3. MOBILE NAVIGATION MENU TOGGLE
     -------------------------------------------------------------------------- */
  const menuToggle = document.getElementById('menu-toggle');
  const navMenu = document.getElementById('nav-menu');

  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      const icon = menuToggle.querySelector('i');
      if (icon) {
        if (navMenu.classList.contains('active')) {
          icon.classList.remove('fa-bars');
          icon.classList.add('fa-xmark');
        } else {
          icon.classList.remove('fa-xmark');
          icon.classList.add('fa-bars');
        }
      }
    });

    // Close mobile menu when clicking any nav link
    const navLinks = navMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        const icon = menuToggle.querySelector('i');
        if (icon) {
          icon.classList.remove('fa-xmark');
          icon.classList.add('fa-bars');
        }
      });
    });
  }

  /* --------------------------------------------------------------------------
     4. GALLERY LIGHTBOX MODAL
     -------------------------------------------------------------------------- */
  const galleryCards = document.querySelectorAll('.gallery-card');
  const lightboxModal = document.getElementById('lightbox-modal');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxCaption = document.getElementById('lightbox-caption');
  const lightboxClose = document.getElementById('lightbox-close');

  if (galleryCards.length > 0 && lightboxModal && lightboxImg) {
    galleryCards.forEach(card => {
      card.addEventListener('click', () => {
        const fullSrc = card.getAttribute('data-full-img') || card.querySelector('img')?.src;
        const title = card.getAttribute('data-title') || card.querySelector('.gallery-title')?.textContent || '';

        if (fullSrc) {
          lightboxImg.src = fullSrc;
          if (lightboxCaption) lightboxCaption.textContent = title;
          lightboxModal.classList.add('active');
          document.body.style.overflow = 'hidden';
        }
      });
    });

    const closeLightbox = () => {
      lightboxModal.classList.remove('active');
      document.body.style.overflow = '';
      if (lightboxImg) lightboxImg.src = '';
    };

    if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
    
    lightboxModal.addEventListener('click', (e) => {
      if (e.target === lightboxModal) closeLightbox();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && lightboxModal.classList.contains('active')) {
        closeLightbox();
      }
    });
  }

  /* --------------------------------------------------------------------------
     5. CONTACT FORM (BOTTOM OF PAGE) WHATSAPP INTEGRATION
     -------------------------------------------------------------------------- */
  const bookingForm = document.getElementById('booking-form');
  if (bookingForm) {
    bookingForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const nameInput = document.getElementById('user-name');
      const phoneInput = document.getElementById('user-phone');
      const goalSelect = document.getElementById('user-goal');

      const name = nameInput ? nameInput.value.trim() : '';
      const phone = phoneInput ? phoneInput.value.trim() : '';
      const goal = goalSelect ? goalSelect.value : 'Bodybuilding & Fitness';

      if (!name || !phone) {
        alert('Please fill in both your full name and contact number.');
        return;
      }

      const encodedMessage = 
        `Hello Muscle Monster Gym! 👋%0A%0A` +
        `I would like to claim my 1-Day Free Workout Pass.%0A%0A` +
        `• Name: *${encodeURIComponent(name)}*%0A` +
        `• Mobile: *${encodeURIComponent(phone)}*%0A` +
        `• Fitness Goal: *${encodeURIComponent(goal)}*%0A%0A` +
        `Please confirm my trial booking at the Haldwani gym.`;

      const whatsappUrl = `https://wa.me/917906120653?text=${encodedMessage}`;
      window.open(whatsappUrl, '_blank');
    });
  }

});
