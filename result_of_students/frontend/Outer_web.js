/**
 * outer_web.js — Academia Landing Page
 *
 * Responsibilities:
 *  1. Filter the institute list as the user types
 *  2. On institute selection → navigate to tmp.html with
 *     query params ?institute=NAME&address=ADDRESS
 *  3. "Change institute" chip button → show overlay again
 */

"use strict";

/* ── DOM refs ────────────────────────────────────────── */
const overlay           = document.getElementById("landingOverlay");
const instituteSearch   = document.getElementById("instituteSearch");
const instituteList     = document.getElementById("instituteList");
const noResults         = document.getElementById("landingNoResults");
const headerChip        = document.getElementById("headerInstituteChip");
const headerInstituteName = document.getElementById("headerInstituteName");
const changeBtn         = document.getElementById("changeInstituteBtn");
const logoBtn           = document.getElementById("logoBtn");

/* ── Live filter ─────────────────────────────────────── */
instituteSearch.addEventListener("input", filterInstitutes);

function filterInstitutes() {
  const query = instituteSearch.value.trim().toLowerCase();
  const items = instituteList.querySelectorAll(".institute-item");
  let visibleCount = 0;

  items.forEach((item) => {
    const name    = (item.dataset.name    || "").toLowerCase();
    const address = (item.dataset.address || "").toLowerCase();
    const matches = !query || name.includes(query) || address.includes(query);

    if (matches) {
      item.removeAttribute("hidden");
      visibleCount++;
    } else {
      item.setAttribute("hidden", "");
    }
  });

  noResults.hidden = visibleCount > 0;
}

/* ── Keyboard navigation within the list ────────────── */
instituteSearch.addEventListener("keydown", (e) => {
  if (e.key === "ArrowDown") {
    e.preventDefault();
    const first = instituteList.querySelector(".institute-item:not([hidden])");
    if (first) first.focus();
  }
});

instituteList.addEventListener("keydown", (e) => {
  const items = [...instituteList.querySelectorAll(".institute-item:not([hidden])")];
  const idx   = items.indexOf(document.activeElement);

  if (e.key === "ArrowDown") {
    e.preventDefault();
    if (idx < items.length - 1) items[idx + 1].focus();
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    if (idx > 0) items[idx - 1].focus();
    else instituteSearch.focus();
  } else if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    if (items[idx]) selectInstitute(items[idx]);
  }
});

/* ── Click on institute row ──────────────────────────── */
instituteList.addEventListener("click", (e) => {
  const item = e.target.closest(".institute-item");
  if (item) selectInstitute(item);
});

/* ── Select an institute and navigate ───────────────── */
function selectInstitute(item) {
  const name    = item.dataset.name    || "";
  const address = item.dataset.address || "";

  /* Animate the overlay out */
  overlay.classList.add("landing-hidden");

  /* Show the chip in the header */
  headerInstituteName.textContent = name;
  headerChip.removeAttribute("hidden");

  /* Navigate to inner web with params */
  const params = new URLSearchParams({ institute: name, address });
  window.location.href = `tmp.html?${params.toString()}`;
}

/* ── Logo button — re-shows the overlay ─────────────── */
logoBtn.addEventListener("click", () => {
  overlay.classList.remove("landing-hidden");
  instituteSearch.value = "";
  filterInstitutes();
  /* Focus the search field */
  setTimeout(() => instituteSearch.focus(), 100);
});

/* ── "Change institute" chip button ─────────────────── */
if (changeBtn) {
  changeBtn.addEventListener("click", () => {
    overlay.classList.remove("landing-hidden");
    instituteSearch.value = "";
    filterInstitutes();
    setTimeout(() => instituteSearch.focus(), 100);
  });
}

/* ── On load: focus the search field ────────────────── */
window.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => instituteSearch.focus(), 200);
});