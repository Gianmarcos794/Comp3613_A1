# COMP 3613 Assignment 2: Test Planning & Implementation

**Name:** _your name_
**ID:** _your ID_
**Repository:** https://github.com/Gianmarcos794/Comp3613_A1

---

## 1. Project Description

**Internship Platform (InternSearch)** is a departmental system that takes student applications and matches them to internship positions offered by participating companies.

InternSearch treats internships as a **matching service run by the department**, not a job board.

- **Students apply to a general pool**, not to a specific posting. Each student has one application: their profile details (program, year, GPA), the kind of role they want, and their projects. The student sees its status: submitted, matched (with the internship title, company and location), or rejected. A rejected application can be edited and resubmitted.
- **Companies are trusted partners.** They cannot register themselves; the Admin creates each company account once the company is approved. A company publishes internships with requirements (program, minimum GPA, minimum year, number of positions, deadline), manages or closes them, and sees the students matched to them.
- **The Admin makes the match, and it is final.** The system always checks requirements first (program, GPA, year, open status, deadline not passed), so the Admin only picks from internships the student is eligible for. If none fit, the Admin rejects the application.
- **Rules that keep it fair:** student sign-up needs a `.edu` university email, GPA is capped at 4.3, an internship closes when its positions are filled, and an internship with matches can only be closed, never deleted.

**Workflows:**

1. Publish/Manage Internships (Company)
2. Submit Application (Student)
3. Match Application to Internship (Admin)

## 2. Use Case Diagram

![Use case diagram](../diagrams/use-case.png)

## 3. Entity Relationship Diagram

![Entity relationship diagram](../diagrams/erd.png)

_Source: `docs/diagrams/erd.mmd`. Export it to `docs/diagrams/erd.png` (for example at https://mermaid.live) so the image above shows up._

## 4. Application Wireframe

![Wireframes for all three workflows](../wireframes/wireframes.png)

---

## 5. Test Plans

### 5.1 User Acceptance Test Plan

Based on the wireframe screens above. Fill in **Actual** and **Result** while you test in the browser.

| ID | Workflow | Wireframe screen | Steps | Expected result | Actual | Result |
|---|---|---|---|---|---|---|
| UAT-01 | | | | | | |

### 5.2 Unit Test Plan

One row per business rule in the services (`app/services/`).

| ID | Service / function | Input / setup | Expected result |
|---|---|---|---|
| UT-01 | | | |

### 5.3 Integration Test Plan

One row per route + scenario (request → route → service → repository → test database).

| ID | Endpoint | Role | Input | Expected response | Expected DB change |
|---|---|---|---|---|---|
| IT-01 | | | | | |

---

## 6. Implementation

- **Repository:** https://github.com/Gianmarcos794/Comp3613_A1
- **Unit tests:** `tests/unit/`
- **Integration tests:** `tests/integration/`
- **API tests:** `postman/` (Postman collection exported to JSON)

Run with:

```bash
pytest tests/unit -v
pytest tests/integration -v
```

---

## 7. Reports

### 7.1 Unit Tests Report

_Screenshot of `pytest tests/unit -v`._

### 7.2 Integration Tests Report

_Screenshot of `pytest tests/integration -v`._

### 7.3 Postman Collection Run Report

_Screenshot of the Postman Collection Runner results._
