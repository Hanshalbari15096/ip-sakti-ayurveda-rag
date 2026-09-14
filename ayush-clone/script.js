/* ============================================================
   script.js — small interactions for the educational clone
   Teaches: event listeners, class toggling, DOM manipulation
   ============================================================ */

// ---- 1. Mobile hamburger menu ----
// Grabs the button and the list, then toggles the "open" class on click.
const navToggle = document.getElementById("navToggle");
const navList = document.getElementById("navList");

navToggle.addEventListener("click", function () {
  navList.classList.toggle("open");
});

// ---- 2. Font size accessibility controls ----
// Increased size by stepping a CSS variable on <body>'s font-size.
let fontSize = 100; // percent
const body = document.body;

document.getElementById("incFont").addEventListener("click", function () {
  fontSize = Math.min(fontSize + 10, 130); // cap at 130%
  body.style.fontSize = fontSize + "%";
});

document.getElementById("decFont").addEventListener("click", function () {
  fontSize = Math.max(fontSize - 10, 80); // floor at 80%
  body.style.fontSize = fontSize + "%";
});
