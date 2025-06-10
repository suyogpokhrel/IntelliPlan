// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Intersection Observer for fade-in animations
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all sections
document.querySelectorAll('.section').forEach(section => {
    section.classList.add('fade-out');
    observer.observe(section);
});

// Add fade-in animation to feature cards
document.querySelectorAll('.feature-card, .solution-card').forEach(card => {
    card.classList.add('fade-out');
    observer.observe(card);
});

document.addEventListener('DOMContentLoaded', () => {
    // Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const verticalNav = document.querySelector('.vertical-nav');
    const mainContent = document.querySelector('.main-content');

    navToggle.addEventListener('click', () => {
        verticalNav.classList.toggle('active');
    });

    // Close nav when clicking outside
    document.addEventListener('click', (e) => {
        if (!verticalNav.contains(e.target) && !navToggle.contains(e.target)) {
            verticalNav.classList.remove('active');
        }
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
            // Close mobile nav after clicking
            if (window.innerWidth <= 1024) {
                verticalNav.classList.remove('active');
            }
        });
    });

    // Floating elements animation
    const floatItems = document.querySelectorAll('.float-item');
    floatItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.5}s`;
    });

    // Parallax effect for hero section
    const hero = document.querySelector('.hero');
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        hero.style.backgroundPositionY = `${scrolled * 0.5}px`;
    });

    // Dynamic year in footer
    document.querySelector('.footer-bottom p').innerHTML = 
        `&copy; ${new Date().getFullYear()} AI-Driven Adaptive Study Planner. All rights reserved.`;

    // Add loading animation for images
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('load', function() {
            this.classList.add('loaded');
        });
    });

    // Add hover effect for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Navigation bar color change on scroll
// window.addEventListener('scroll', function() {
//     const nav = document.querySelector('nav');
//     if (window.scrollY > 50) {
//         nav.style.background = '#ffffff';
//         nav.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
//     } else {
//         nav.style.background = 'transparent';
//         nav.style.boxShadow = 'none';
//     }
// }); 