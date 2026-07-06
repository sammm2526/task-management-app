// Wait for the DOM (Document Object Model) to be fully loaded before running our script
document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 1. MOBILE NAVBAR TOGGLE MENU
    // ==========================================
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        // Add a click event listener to the hamburger button
        navToggle.addEventListener('click', () => {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Close the menu when any nav link is clicked
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }

    // ==========================================
    // 2. AUTO-DISMISS FLASH ALERTS (3 Seconds)
    // ==========================================
    // Find all flash alert boxes on the page
    const flashAlerts = document.querySelectorAll('.flash-alert');
    
    flashAlerts.forEach(alert => {
        // We set a timer to trigger after 3000 milliseconds (3 seconds)
        setTimeout(() => {
            // Apply CSS transition properties for a smooth fadeout
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease, margin-bottom 0.5s ease, padding 0.5s ease, height 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            
            // Wait for the 0.5-second fadeout transition to complete, then remove the element from the page layout
            setTimeout(() => {
                alert.style.padding = '0';
                alert.style.height = '0';
                alert.style.overflow = 'hidden';
                alert.style.border = 'none';
                alert.style.marginBottom = '0';
                setTimeout(() => {
                    alert.remove();
                }, 100);
            }, 500);
        }, 3000);
    });
});
