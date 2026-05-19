/**
 * app.js — Academia Student Search Dashboard
 * - Nepali B.S. year-based filtering (no date picker)
 * - Logo click → page reset / refresh
 * - Dynamic table rendering + pagination
 */

"use strict";

/* ── Config ──────────────────────────────────────────── */
const PAGE_SIZE = 8;

/* ── Mock dataset ────────────────────────────────────── */
/* passing_year uses Nepali Bikram Sambat (B.S.) years   */
const MOCK_STUDENTS = [
  { name: "Ananya Sharma",     passing_year: 2080, gpa: 3.9,  major: "Computer Science"    },
  { name: "Rajan Thapa",       passing_year: 2080, gpa: 3.4,  major: "Business Admin"      },
  { name: "Priya Mehta",       passing_year: 2079, gpa: 3.7,  major: "Electrical Eng."     },
  { name: "Ali Hassan",        passing_year: 2080, gpa: 2.8,  major: "Mathematics"         },
  { name: "Sofia Koirala",     passing_year: 2079, gpa: 3.6,  major: "Psychology"          },
  { name: "Dev Patel",         passing_year: 2081, gpa: 3.2,  major: "Chemistry"           },
  { name: "Lena Fischer",      passing_year: 2080, gpa: 3.8,  major: "Biology"             },
  { name: "Omar Al-Amin",      passing_year: 2079, gpa: 3.0,  major: "Physics"             },
  { name: "Yuki Nakamura",     passing_year: 2080, gpa: 3.95, major: "Data Science"        },
  { name: "Maria Gonzalez",    passing_year: 2079, gpa: 2.6,  major: "History"             },
  { name: "James Okonkwo",     passing_year: 2081, gpa: 3.5,  major: "Economics"           },
  { name: "Fatima Al-Rashid",  passing_year: 2080, gpa: 3.85, major: "Medicine"            },
  { name: "Lucas Weber",       passing_year: 2079, gpa: 3.1,  major: "Architecture"        },
  { name: "Nisha Adhikari",    passing_year: 2080, gpa: 3.75, major: "Law"                 },
  { name: "Carlos Mendes",     passing_year: 2079, gpa: 2.9,  major: "Sociology"           },
  { name: "Aisha Kamara",      passing_year: 2081, gpa: 3.6,  major: "Computer Science"    },
  { name: "Takeshi Mori",      passing_year: 2080, gpa: 3.3,  major: "Mechanical Eng."     },
  { name: "Ingrid Hansen",     passing_year: 2079, gpa: 3.55, major: "Environmental Sci."  },
  { name: "Bikash Rai",        passing_year: 2081, gpa: 3.45, major: "Civil Eng."          },
  { name: "Sita Gurung",       passing_year: 2081, gpa: 3.88, major: "Nursing"             },
];

/* ── State ───────────────────────────────────────────── */
let currentPage = 1;
let currentData = [];

/* ── DOM refs ────────────────────────────────────────── */
const form        = document.getElementById("searchForm");
const nameInput   = document.getElementById("nameInput");
const yearInput   = document.getElementById("yearInput");
const messageArea = document.getElementById("messageArea");
const tableBody   = document.getElementById("tableBody");
const prevBtn     = document.getElementById("prevBtn");
const nextBtn     = document.getElementById("nextBtn");
const pageInfo    = document.getElementById("pageInfo");
const logoBtn     = document.getElementById("logoBtn");

/* ── Logo → refresh / reset ──────────────────────────── */
logoBtn.addEventListener("click", () => {
  /* Reset form fields */
  nameInput.value = "";
  yearInput.value = "";
  /* Clear table and messages */
  clearTable();
  clearMessage();
  resetPagination();
  currentData = [];
  /* Smooth scroll to top */
  window.scrollTo({ top: 0, behavior: "smooth" });
});

/* ── Form submit ─────────────────────────────────────── */
form.addEventListener("submit", handleSearch);
prevBtn.addEventListener("click", () => changePage(currentPage - 1));
nextBtn.addEventListener("click", () => changePage(currentPage + 1));

/* ── handleSearch ────────────────────────────────────── */
async function handleSearch(event) {
  event.preventDefault();

  const name = nameInput.value.trim();
  const year = yearInput.value.trim(); /* e.g. "2080" or "" */

  showLoading("Searching the registry…");
  clearTable();
  resetPagination();

  try {
    const results = await fetchStudents(name, year ? parseInt(year, 10) : null);
    currentData = results;
    currentPage = 1;

    if (results.length === 0) {
      showMessage("info", "No students matched your search criteria.");
    } else {
      showMessage("success", `Found ${results.length} student${results.length !== 1 ? "s" : ""}.`);
      renderPage(currentPage);
      updatePagination();
    }
  } catch (err) {
    console.error(err);
    showMessage("error", "Could not connect to the server. Please try again later.");
  }
}

/* ── fetchStudents (mock — swap for real fetch) ──────── */
/**
 * To connect a real backend replace this function body with:
 *
 *   const res = await fetch(
 *     `/api/students?name=${encodeURIComponent(name)}&year=${year ?? ""}`
 *   );
 *   if (!res.ok) throw new Error("Network error");
 *   return await res.json();
 */
function fetchStudents(name, year) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      try {
        const results = MOCK_STUDENTS.filter((s) => {
          const matchName = name
            ? s.name.toLowerCase().includes(name.toLowerCase())
            : true;
          const matchYear = year !== null ? s.passing_year === year : true;
          return matchName && matchYear;
        });
        resolve(results);
      } catch (e) {
        reject(e);
      }
    }, 650);
  });
}

/* ── renderPage ──────────────────────────────────────── */
function renderPage(page) {
  clearTable();

  const start = (page - 1) * PAGE_SIZE;
  const slice = currentData.slice(start, start + PAGE_SIZE);
  if (slice.length === 0) return;

  const fragment = document.createDocumentFragment();

  slice.forEach((student) => {
    const tr = document.createElement("tr");

    const tdName = document.createElement("td");
    tdName.textContent = student.name;

    const tdYear = document.createElement("td");
    tdYear.textContent = `${student.passing_year} B.S.`;

    const tdGpa = document.createElement("td");
    const pill  = document.createElement("span");
    pill.classList.add("gpa-pill", gpaClass(student.gpa));
    pill.textContent = student.gpa.toFixed(2);
    tdGpa.appendChild(pill);

    const tdMajor = document.createElement("td");
    tdMajor.textContent = student.major;

    tr.appendChild(tdName);
    tr.appendChild(tdYear);
    tr.appendChild(tdGpa);
    tr.appendChild(tdMajor);
    fragment.appendChild(tr);
  });

  tableBody.appendChild(fragment);
}

/* ── Pagination ──────────────────────────────────────── */
function changePage(page) {
  const total = Math.ceil(currentData.length / PAGE_SIZE);
  if (page < 1 || page > total) return;
  currentPage = page;
  renderPage(currentPage);
  updatePagination();
}
function updatePagination() {
  const total = Math.ceil(currentData.length / PAGE_SIZE);
  pageInfo.textContent  = `Page ${currentPage} of ${total}`;
  prevBtn.disabled = currentPage <= 1;
  nextBtn.disabled = currentPage >= total;
}
function resetPagination() {
  currentPage = 1;
  prevBtn.disabled = true;
  nextBtn.disabled = true;
  pageInfo.textContent = "Page 1";
}

/* ── Messages ────────────────────────────────────────── */
function showLoading(text) {
  clearMessage();
  const div = document.createElement("div");
  div.className = "msg msg--loading";
  div.setAttribute("role", "status");
  const spinner = document.createElement("span");
  spinner.className = "spinner";
  spinner.setAttribute("aria-hidden", "true");
  div.appendChild(spinner);
  div.appendChild(document.createTextNode(text));
  messageArea.appendChild(div);
}

function showMessage(type, text) {
  clearMessage();
  const div = document.createElement("div");
  div.className = `msg msg--${type}`;
  const icon = createMsgIcon(type);
  if (icon) div.appendChild(icon);
  div.appendChild(document.createTextNode(text));
  messageArea.appendChild(div);
}

function clearMessage() {
  while (messageArea.firstChild) messageArea.removeChild(messageArea.firstChild);
}

function createMsgIcon(type) {
  const ns  = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 20 20");
  svg.setAttribute("fill", "none");
  svg.setAttribute("aria-hidden", "true");
  svg.style.cssText = "width:18px;height:18px;flex-shrink:0";

  const path = document.createElementNS(ns, "path");
  path.setAttribute("stroke", "currentColor");
  path.setAttribute("stroke-width", "1.8");
  path.setAttribute("stroke-linecap", "round");
  path.setAttribute("stroke-linejoin", "round");

  if (type === "success") {
    path.setAttribute("d", "M4 10l4 4 8-8");
  } else if (type === "error") {
    path.setAttribute("d", "M6 6l8 8M14 6l-8 8");
  } else {
    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", "10"); circle.setAttribute("cy", "10");
    circle.setAttribute("r", "8");
    circle.setAttribute("stroke", "currentColor");
    circle.setAttribute("stroke-width", "1.5");
    svg.appendChild(circle);
    path.setAttribute("d", "M10 7v1M10 10v4");
  }
  svg.appendChild(path);
  return svg;
}

/* ── Table helpers ───────────────────────────────────── */
function clearTable() {
  while (tableBody.firstChild) tableBody.removeChild(tableBody.firstChild);
}

/* ── GPA class ───────────────────────────────────────── */
function gpaClass(gpa) {
  if (gpa >= 3.5) return "gpa-pill--high";
  if (gpa >= 3.0) return "gpa-pill--mid";
  return "gpa-pill--low";
}