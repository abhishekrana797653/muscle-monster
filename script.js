/**
 * MUSCLE MONSTER GYM — SCRIPT.JS
 * Implements dramatic scroll-triggered counter animations, interactive lightbox,
 * mobile navigation, and WhatsApp booking integration.
 */

document.addEventListener('DOMContentLoaded', () => {

  /* --------------------------------------------------------------------------
     1. DRAMATIC SCROLL-TRIGGERED COUNTER ANIMATION
     -------------------------------------------------------------------------- */
  const counters = document.querySelectorAll('.counter-animate');
  
  if (counters.length > 0) {
    // Ease-out cubic function for a dramatic deceleration curve
    const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

    const animateCounter = (counterElement) => {
      const target = parseFloat(counterElement.getAttribute('data-target')) || 0;
      const suffix = counterElement.getAttribute('data-suffix') || '';
      const prefix = counterElement.getAttribute('data-prefix') || '';
      const duration = parseInt(counterElement.getAttribute('data-duration'), 10) || 2200; // ms
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
          // Final exact number with suffix
          counterElement.textContent = `${prefix}${target}${suffix}`;
        }
      };

      window.requestAnimationFrame(step);
    };

    // IntersectionObserver to trigger animation when scrolled into view
    const counterObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          animateCounter(el);
          observer.unobserve(el); // Only animate once
        }
      });
    }, {
      threshold: 0.35, // Trigger when 35% visible
      rootMargin: '0px 0px -50px 0px'
    });

    counters.forEach(counter => {
      counter.textContent = '0'; // Initialize at 0
      counterObserver.observe(counter);
    });
  }

  /* --------------------------------------------------------------------------
     2. STICKY HEADER SCROLL EFFECT
     -------------------------------------------------------------------------- */
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 40) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    }, { passive: true });
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

    // Close menu when clicking nav links
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
          document.body.style.overflow = 'hidden'; // lock background scrolling
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
      if (e.target === lightboxModal) {
        closeLightbox();
      }
    });

    // Escape key listener
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && lightboxModal.classList.contains('active')) {
        closeLightbox();
      }
    });
  }

  /* --------------------------------------------------------------------------
     5. WHATSAPP BOOKING FORM INTEGRATION
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
      const goal = goalSelect ? goalSelect.value : 'General Fitness';

      if (!name || !phone) {
        alert('Please fill in both your full name and contact number.');
        return;
      }

      const encodedMessage = 
        `Hello Muscle Monster Gym! 👋%0A%0A` +
        `I would like to book my 1st Free Class / Training Assessment.%0A%0A` +
        `• Name: *${encodeURIComponent(name)}*%0A` +
        `• Mobile: *${encodeURIComponent(phone)}*%0A` +
        `• Target Goal: *${encodeURIComponent(goal)}*%0A%0A` +
        `Please confirm available slots at the Haldwani facility.`;

      const whatsappUrl = `https://wa.me/917906120653?text=${encodedMessage}`;
      window.open(whatsappUrl, '_blank');
    });
  }

});
