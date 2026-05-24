/**
 * tmp.js — Academia Student Search Dashboard
 * Features:
 *  - Search by name + Nepali B.S. year
 *  - After search: panel shifts left 45%, marksheet appears right 55%
 *  - Click a table row → populate that student's marksheet
 *  - Logo resets everything
 */

"use strict";

/* ── Config ──────────────────────────────────────────── */
const PAGE_SIZE = 8;

/* ── Subject templates per major ─────────────────────── */
/* Each subject: { code, name, creditHours, gradePoint, grade, finalGrade } */
const SUBJECT_TEMPLATES = {
  "Computer Science": [
    { code: "CS101", name: "Introduction to Programming",    cr: 3 },
    { code: "CS102", name: "Data Structures & Algorithms",   cr: 3 },
    { code: "CS201", name: "Database Management Systems",    cr: 3 },
    { code: "CS202", name: "Operating Systems",              cr: 3 },
    { code: "CS301", name: "Computer Networks",              cr: 3 },
    { code: "MATH101", name: "Discrete Mathematics",         cr: 3 },
  ],
  "Business Admin": [
    { code: "BA101", name: "Principles of Management",       cr: 3 },
    { code: "BA102", name: "Business Communication",         cr: 3 },
    { code: "BA201", name: "Financial Accounting",           cr: 3 },
    { code: "BA202", name: "Marketing Management",           cr: 3 },
    { code: "BA301", name: "Business Law",                   cr: 3 },
    { code: "ECON101", name: "Microeconomics",               cr: 3 },
  ],
  "default": [
    { code: "GEN101", name: "English Communication",         cr: 3 },
    { code: "GEN102", name: "Mathematics",                   cr: 3 },
    { code: "GEN201", name: "Research Methodology",          cr: 3 },
    { code: "GEN202", name: "Environmental Science",         cr: 3 },
    { code: "GEN301", name: "Core Subject I",                cr: 3 },
    { code: "GEN302", name: "Core Subject II",               cr: 3 },
  ],
};

/* Grade point → letter grade mapping */
const GP_TO_LETTER = (gp) => {
  if (gp >= 3.7) return "A+";
  if (gp >= 3.3) return "A";
  if (gp >= 3.0) return "A-";
  if (gp >= 2.7) return "B+";
  if (gp >= 2.3) return "B";
  if (gp >= 2.0) return "B-";
  if (gp >= 1.7) return "C+";
  if (gp >= 1.0) return "C";
  return "F";
};

/* Derive subject-level grade points from student GPA (with small variance) */
function buildSubjectGrades(student) {
  const templates = SUBJECT_TEMPLATES[student.major] || SUBJECT_TEMPLATES["default"];
  return templates.map((subj, i) => {
    /* Add slight variance: alternates ±0.1 to ±0.2 */
    const variance = (i % 2 === 0 ? 1 : -1) * (0.1 + (i % 3) * 0.05);
    const gp = Math.min(4.0, Math.max(0.0, +(student.gpa + variance).toFixed(2)));
    const letter = GP_TO_LETTER(gp);
    const finalGrade = letter === "F" ? "FAIL" : "PASS";
    const total = +(gp * subj.cr).toFixed(2);
    return { ...subj, gradePoint: gp, grade: letter, finalGrade, total };
  });
}

/* Generate a plausible DOB from the student's passing year
   Assumes ~17-18 years old at graduation (grade 10) */
function generateDOB(student) {
  /* Convert B.S. passing year approx to A.D. (subtract 56/57) */
  const adYear = student.passing_year - 57;
  const birthYear = adYear - 17;
  /* Use student name length as a seed for month/day variety */
  const month = ((student.name.length * 3) % 12) + 1;
  const day   = ((student.name.length * 7) % 28) + 1;
  return `${String(day).padStart(2,"0")}/${String(month).padStart(2,"0")}/${birthYear}`;
}

/* ── Mock dataset ────────────────────────────────────── */
const MOCK_STUDENTS = [
  { name: "Ananya Sharma",    passing_year: 2080, gpa: 3.90, major: "Computer Science"   },
  { name: "Rajan Thapa",      passing_year: 2080, gpa: 3.40, major: "Business Admin"     },
  { name: "Priya Mehta",      passing_year: 2079, gpa: 3.70, major: "Electrical Eng."    },
  { name: "Ali Hassan",       passing_year: 2080, gpa: 2.80, major: "Mathematics"        },
  { name: "Sofia Koirala",    passing_year: 2079, gpa: 3.60, major: "Psychology"         },
  { name: "Dev Patel",        passing_year: 2081, gpa: 3.20, major: "Chemistry"          },
  { name: "Lena Fischer",     passing_year: 2080, gpa: 3.80, major: "Biology"            },
  { name: "Omar Al-Amin",     passing_year: 2079, gpa: 3.00, major: "Physics"            },
  { name: "Yuki Nakamura",    passing_year: 2080, gpa: 3.95, major: "Computer Science"   },
  { name: "Maria Gonzalez",   passing_year: 2079, gpa: 2.60, major: "default"            },
  { name: "James Okonkwo",    passing_year: 2081, gpa: 3.50, major: "Business Admin"     },
  { name: "Fatima Al-Rashid", passing_year: 2080, gpa: 3.85, major: "default"            },
  { name: "Lucas Weber",      passing_year: 2079, gpa: 3.10, major: "default"            },
  { name: "Nisha Adhikari",   passing_year: 2080, gpa: 3.75, major: "default"            },
  { name: "Carlos Mendes",    passing_year: 2079, gpa: 2.90, major: "default"            },
  { name: "Aisha Kamara",     passing_year: 2081, gpa: 3.60, major: "Computer Science"   },
  { name: "Takeshi Mori",     passing_year: 2080, gpa: 3.30, major: "default"            },
  { name: "Ingrid Hansen",    passing_year: 2079, gpa: 3.55, major: "default"            },
  { name: "Bikash Rai",       passing_year: 2081, gpa: 3.45, major: "default"            },
  { name: "Sita Gurung",      passing_year: 2081, gpa: 3.88, major: "default"            },
];

/* ── State ───────────────────────────────────────────── */
let currentPage    = 1;
let currentData    = [];
let activeStudent  = null;
let activeRow      = null;

/* ── DOM refs ────────────────────────────────────────── */
const form         = document.getElementById("searchForm");
const nameInput    = document.getElementById("nameInput");
const dobInput     = document.getElementById("dobInput");
const yearInput    = document.getElementById("yearInput");
const messageArea  = document.getElementById("messageArea");
const tableBody    = document.getElementById("tableBody");
const prevBtn      = document.getElementById("prevBtn");
const nextBtn      = document.getElementById("nextBtn");
const pageInfo     = document.getElementById("pageInfo");
const logoBtn      = document.getElementById("logoBtn");
const contentArea  = document.getElementById("contentArea");
const marksheetPanel = document.getElementById("marksheetPanel");

/* Marksheet field refs */
const msStudentName  = document.getElementById("ms-student-name");
const msDob          = document.getElementById("ms-dob");
const msDobAd        = document.getElementById("ms-dob-ad");
const msRegNo        = document.getElementById("ms-reg-no");
const msSymbolNo     = document.getElementById("ms-symbol-no");
const msExamYear     = document.getElementById("ms-exam-year");
const msExamYearAd   = document.getElementById("ms-exam-year-ad");
const msGradesBody   = document.getElementById("ms-grades-body");
const msTotalCr      = document.getElementById("ms-total-cr");
const msCgpa         = document.getElementById("ms-cgpa");
const msIssueDate    = document.getElementById("ms-issue-date");

/* ── Name input: letters + spaces only, auto-uppercase ── */
nameInput.addEventListener("input", () => {
  const pos = nameInput.selectionStart;
  /* Strip anything that isn't a letter or space */
  const clean = nameInput.value.replace(/[^a-zA-Z\s]/g, "").toUpperCase();
  if (nameInput.value !== clean) {
    nameInput.value = clean;
    /* Restore cursor position after value change */
    nameInput.setSelectionRange(pos, pos);
  }
});
nameInput.addEventListener("keydown", (e) => {
  /* Block digits and symbols at the keydown level for immediate feedback */
  if (e.key.length === 1 && /[^a-zA-Z\s]/.test(e.key)) {
    e.preventDefault();
  }
});

/* ── DOB input: auto-format as DD/MM/YYYY ────────────── */
dobInput.addEventListener("input", (e) => {
  /* Strip everything except digits */
  let raw = dobInput.value.replace(/\D/g, "");
  /* Limit to 8 digits (DDMMYYYY) */
  if (raw.length > 8) raw = raw.slice(0, 8);
  /* Insert slashes */
  let formatted = raw;
  if (raw.length > 4) {
    formatted = raw.slice(0, 2) + "/" + raw.slice(2, 4) + "/" + raw.slice(4);
  } else if (raw.length > 2) {
    formatted = raw.slice(0, 2) + "/" + raw.slice(2);
  }
  dobInput.value = formatted;
});
dobInput.addEventListener("keydown", (e) => {
  /* Only allow digits, backspace, delete, arrow keys, tab */
  if (
    e.key.length === 1 &&
    !/\d/.test(e.key)
  ) {
    e.preventDefault();
  }
});

/* ── Seed empty marksheet on load ────────────────────── */
(function seedEmptyMarksheet() {
  const frag = document.createDocumentFragment();
  for (let i = 0; i < 10; i++) {
    const tr = document.createElement("tr");
    tr.className = "ms-empty-row";
    for (let j = 0; j < 7; j++) {
      const td = document.createElement("td");
      td.textContent = "\u00a0";
      tr.appendChild(td);
    }
    frag.appendChild(tr);
  }
  document.getElementById("ms-grades-body").appendChild(frag);
})();

/* ── Logo → full reset ───────────────────────────────── */
logoBtn.addEventListener("click", () => {
  nameInput.value = "";
  dobInput.value  = "";
  yearInput.value = "";
  clearTable();
  clearMessage();
  resetPagination();
  currentData   = [];
  activeStudent = null;
  activeRow     = null;
  contentArea.classList.remove("has-results");
  marksheetPanel.setAttribute("aria-hidden", "true");
  clearMarksheet();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

/* ── Form submit ─────────────────────────────────────── */
form.addEventListener("submit", handleSearch);
prevBtn.addEventListener("click", () => changePage(currentPage - 1));
nextBtn.addEventListener("click", () => changePage(currentPage + 1));

async function handleSearch(event) {
  event.preventDefault();

  const name = nameInput.value.trim();
  const dob  = dobInput.value.trim();
  const year = yearInput.value.trim();

  showLoading("Searching the registry…");
  clearTable();
  resetPagination();
  contentArea.classList.remove("has-results");
  marksheetPanel.setAttribute("aria-hidden", "true");
  clearMarksheet();
  activeStudent = null;
  activeRow     = null;

  try {
    const results = await fetchStudents(name, dob, year ? parseInt(year, 10) : null);
    currentData = results;
    currentPage = 1;

    if (results.length === 0) {
      showMessage("info", "No students matched your search criteria.");
    } else {
      showMessage("success", `Found ${results.length} student${results.length !== 1 ? "s" : ""}. Click a row to view marksheet.`);
      renderPage(currentPage);
      updatePagination();
      contentArea.classList.add("has-results");
      marksheetPanel.setAttribute("aria-hidden", "false");
      const firstRow = tableBody.querySelector("tr");
      if (firstRow) firstRow.click();
    }
  } catch (err) {
    console.error(err);
    showMessage("error", "Could not connect to the server. Please try again later.");
  }
}

/* ── Fetch (mock) ────────────────────────────────────── */
function fetchStudents(name, dob, year) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      try {
        const results = MOCK_STUDENTS.filter((s) => {
          const matchName = name
            ? s.name.toUpperCase().includes(name.toUpperCase())
            : true;
          const matchDob = dob
            ? generateDOB(s) === dob
            : true;
          const matchYear = year !== null ? s.passing_year === year : true;
          return matchName && matchDob && matchYear;
        });
        resolve(results);
      } catch (e) { reject(e); }
    }, 650);
  });
}

/* ── Render table page ───────────────────────────────── */
function renderPage(page) {
  clearTable();
  const start = (page - 1) * PAGE_SIZE;
  const slice = currentData.slice(start, start + PAGE_SIZE);
  if (slice.length === 0) return;

  const fragment = document.createDocumentFragment();

  slice.forEach((student) => {
    const tr = document.createElement("tr");
    tr.setAttribute("tabindex", "0");
    tr.setAttribute("role", "button");
    tr.setAttribute("aria-label", `View marksheet for ${student.name}`);

    const tdName = document.createElement("td");
    tdName.textContent = student.name;

    const tdYear = document.createElement("td");
    tdYear.textContent = `${student.passing_year} B.S.`;

    const tdGpa = document.createElement("td");
    const pill = document.createElement("span");
    pill.classList.add("gpa-pill", gpaClass(student.gpa));
    pill.textContent = student.gpa.toFixed(2);
    tdGpa.appendChild(pill);

    const tdMajor = document.createElement("td");
    tdMajor.textContent = student.major === "default" ? "General" : student.major;

    tr.appendChild(tdName);
    tr.appendChild(tdYear);
    tr.appendChild(tdGpa);
    tr.appendChild(tdMajor);

    /* Click / keyboard → show marksheet */
    tr.addEventListener("click", () => selectStudent(student, tr));
    tr.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectStudent(student, tr); }
    });

    fragment.appendChild(tr);
  });

  tableBody.appendChild(fragment);
}

/* ── Select student → fill NEB grade sheet ───────────── */
function selectStudent(student, row) {
  /* Highlight row */
  if (activeRow) activeRow.classList.remove("active-row");
  activeRow = row;
  row.classList.add("active-row");
  activeStudent = student;

  /* Build subject grades */
  const subjects = buildSubjectGrades(student);
  const totalCr  = subjects.reduce((s, sub) => s + sub.cr, 0);
  const totalWt  = subjects.reduce((s, sub) => s + sub.total, 0);
  const cgpa     = (totalWt / totalCr).toFixed(2);

  /* Derive dates */
  const dobBS = generateDOB(student);          /* e.g. 04/07/1989 */
  const dobAD = bsDateToAd(dobBS);             /* approx A.D.     */
  const examYearAD = student.passing_year - 57;

  /* Reg / symbol: deterministic from name */
  const seed    = student.name.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  const regNo   = `REG-${(seed * 13) % 90000 + 10000}`;
  const symNo   = `${(seed * 7) % 9000 + 1000}`;

  /* Today as issue date */
  const today = new Date();
  const issueDate = `${String(today.getDate()).padStart(2,"0")}/${String(today.getMonth()+1).padStart(2,"0")}/${today.getFullYear()}`;

  /* Fill fields */
  msStudentName.textContent = student.name;
  msDob.textContent         = dobBS;
  msDobAd.textContent       = dobAD;
  msRegNo.textContent       = regNo;
  msSymbolNo.textContent    = symNo;
  msExamYear.textContent    = student.passing_year;
  msExamYearAd.textContent  = examYearAD;
  msIssueDate.textContent   = issueDate;

  /* Fill grades table — always 10 rows, empty rows for padding */
  while (msGradesBody.firstChild) msGradesBody.removeChild(msGradesBody.firstChild);
  const frag = document.createDocumentFragment();
  const TOTAL_ROWS = 10;

  for (let i = 0; i < TOTAL_ROWS; i++) {
    const tr = document.createElement("tr");
    const sub = subjects[i] || null;

    if (sub) {
      const vals = [sub.code, sub.name, sub.cr, sub.gradePoint.toFixed(2), sub.grade, sub.finalGrade, ""];
      vals.forEach((val, idx) => {
        const td = document.createElement("td");
        if (idx === 1) td.className = "ms-subject-name";
        td.textContent = val;
        tr.appendChild(td);
      });
    } else {
      /* Empty padding row */
      tr.className = "ms-empty-row";
      for (let j = 0; j < 7; j++) {
        const td = document.createElement("td");
        td.textContent = "\u00a0"; /* non-breaking space keeps row height */
        tr.appendChild(td);
      }
    }
    frag.appendChild(tr);
  }
  msGradesBody.appendChild(frag);

  /* Fill totals */
  msTotalCr.textContent = totalCr;
  msCgpa.textContent    = cgpa;

  marksheetPanel.setAttribute("aria-hidden", "false");
}

/* ── B.S. date → approx A.D. ─────────────────────────── */
function bsDateToAd(bsDate) {
  /* bsDate format: DD/MM/YYYY (B.S.) */
  const parts = bsDate.split("/");
  if (parts.length !== 3) return "—";
  const adYear = parseInt(parts[2], 10) + 57; /* rough conversion */
  return `${parts[0]}/${parts[1]}/${adYear}`;
}

/* ── Clear marksheet ─────────────────────────────────── */
function clearMarksheet() {
  msStudentName.textContent = "................................";
  msDob.textContent         = "........................";
  msDobAd.textContent       = "........................";
  msRegNo.textContent       = "........................";
  msSymbolNo.textContent    = "................";
  msExamYear.textContent    = "............";
  msExamYearAd.textContent  = "............";
  msIssueDate.textContent   = ".....................";
  while (msGradesBody.firstChild) msGradesBody.removeChild(msGradesBody.firstChild);
  /* Re-seed 10 empty rows */
  const frag = document.createDocumentFragment();
  for (let i = 0; i < 10; i++) {
    const tr = document.createElement("tr");
    tr.className = "ms-empty-row";
    for (let j = 0; j < 7; j++) {
      const td = document.createElement("td");
      td.textContent = "\u00a0";
      tr.appendChild(td);
    }
    frag.appendChild(tr);
  }
  msGradesBody.appendChild(frag);
  msTotalCr.textContent = "";
  msCgpa.textContent    = "";
}

/* ── Pagination ──────────────────────────────────────── */
function changePage(page) {
  const total = Math.ceil(currentData.length / PAGE_SIZE);
  if (page < 1 || page > total) return;
  currentPage = page;
  renderPage(currentPage);
  updatePagination();
  /* Re-select first row of new page */
  const firstRow = tableBody.querySelector("tr");
  if (firstRow) firstRow.click();
}
function updatePagination() {
  const total = Math.ceil(currentData.length / PAGE_SIZE);
  pageInfo.textContent = `Page ${currentPage} of ${total}`;
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
  svg.style.cssText = "width:17px;height:17px;flex-shrink:0";
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
    const c = document.createElementNS(ns, "circle");
    c.setAttribute("cx","10"); c.setAttribute("cy","10"); c.setAttribute("r","8");
    c.setAttribute("stroke","currentColor"); c.setAttribute("stroke-width","1.5");
    svg.appendChild(c);
    path.setAttribute("d", "M10 7v1M10 10v4");
  }
  svg.appendChild(path);
  return svg;
}

/* ── Helpers ─────────────────────────────────────────── */
function clearTable() {
  while (tableBody.firstChild) tableBody.removeChild(tableBody.firstChild);
}
function gpaClass(gpa) {
  if (gpa >= 3.5) return "gpa-pill--high";
  if (gpa >= 3.0) return "gpa-pill--mid";
  return "gpa-pill--low";
}