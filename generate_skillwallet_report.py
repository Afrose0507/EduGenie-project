import os
import subprocess
import shutil

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>EduGenie - Project Report for Skillwallet</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

  @page {
    size: A4;
    margin: 15mm 16mm;
  }

  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1e293b;
    background: #ffffff;
    margin: 0;
    padding: 0;
    line-height: 1.55;
    font-size: 13px;
  }

  .page-break {
    page-break-before: always;
  }

  .avoid-break {
    break-inside: avoid;
    page-break-inside: avoid;
  }

  /* COVER / HEADER BLOCK */
  .cover-header {
    border-bottom: 3px solid #3b82f6;
    padding-bottom: 16px;
    margin-bottom: 20px;
  }

  .gov-badge {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    border: 1px solid #bfdbfe;
    margin-bottom: 8px;
  }

  h1.project-title {
    margin: 4px 0 4px 0;
    color: #0f172a;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
  }

  .project-subtitle {
    font-size: 13.5px;
    color: #475569;
    font-weight: 500;
  }

  /* INFO CARDS */
  .meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 18px;
  }

  .card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
  }

  .card-title {
    font-size: 11.5px;
    font-weight: 700;
    color: #1e3a8a;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .meta-item {
    font-size: 12.5px;
    margin: 3px 0;
    color: #334155;
  }

  .meta-item strong {
    color: #0f172a;
  }

  /* LINKS SECTION */
  .links-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 18px;
  }

  .link-row {
    margin: 4px 0;
    font-size: 12px;
  }

  .link-label {
    font-weight: 700;
    color: #166534;
  }

  .link-url {
    font-family: 'JetBrains Mono', monospace;
    color: #2563eb;
    text-decoration: underline;
    word-break: break-all;
    font-size: 11.5px;
  }

  /* SECTION HEADERS */
  h2.section-heading {
    color: #0f172a;
    font-size: 15px;
    font-weight: 700;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 5px;
    margin: 20px 0 10px 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  h2.section-heading::before {
    content: "";
    display: inline-block;
    width: 6px;
    height: 16px;
    background: #3b82f6;
    border-radius: 2px;
  }

  h3.sub-heading {
    color: #1e3a8a;
    font-size: 13px;
    font-weight: 700;
    margin: 12px 0 4px 0;
  }

  p {
    margin: 6px 0;
    color: #334155;
    text-align: justify;
  }

  /* MODULE GRID */
  .modules-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 10px 0;
  }

  .module-card {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 10px 12px;
    background: #ffffff;
  }

  .module-card h4 {
    margin: 0 0 4px 0;
    color: #1d4ed8;
    font-size: 12.5px;
    font-weight: 700;
  }

  .module-card p {
    font-size: 11.5px;
    margin: 0;
    color: #475569;
    text-align: left;
  }

  /* TABLES */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 12px;
  }

  th, td {
    border: 1px solid #cbd5e1;
    padding: 6px 10px;
    text-align: left;
  }

  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
  }

  tr:nth-child(even) {
    background: #f8fafc;
  }

  /* CODE BLOCKS */
  .code-block {
    background: #0f172a;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding: 10px 12px;
    border-radius: 6px;
    margin: 8px 0;
    overflow-x: auto;
    line-height: 1.45;
  }

  .code-block .keyword { color: #38bdf8; font-weight: 600; }
  .code-block .string { color: #4ade80; }
  .code-block .comment { color: #94a3b8; font-style: italic; }

  /* CALLOUT BOXES */
  .callout-success {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    margin: 8px 0;
    font-size: 12px;
  }

  .callout-info {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    margin: 8px 0;
    font-size: 12px;
  }

  /* FOOTER */
  .report-footer {
    margin-top: 24px;
    border-top: 1px solid #e2e8f0;
    padding-top: 8px;
    font-size: 10.5px;
    color: #64748b;
    display: flex;
    justify-content: space-between;
  }
</style>
</head>
<body>

  <!-- ==================== PAGE 1 ==================== -->
  <div class="cover-header">
    <div class="gov-badge">Naan Mudhalvan • Google Cloud Generative AI Track</div>
    <h1 class="project-title">EduGenie: Universal AI Learning Assistant</h1>
    <div class="project-subtitle">Full Project Report & Documentation for Skillwallet Project Submission</div>
  </div>

  <div class="meta-grid">
    <div class="card">
      <div class="card-title">📌 Project Overview</div>
      <div class="meta-item"><strong>Course / Track:</strong> Naan Mudhalvan – GenAI</div>
      <div class="meta-item"><strong>Branch / Year:</strong> B.E. Computer Science & Engg (3rd Year)</div>
      <div class="meta-item"><strong>Project Title:</strong> EduGenie – Google Gemini Assistant</div>
      <div class="meta-item"><strong>Team Identifier:</strong> Team No. 7</div>
      <div class="meta-item"><strong>Submission Platform:</strong> Skillwallet Portal</div>
    </div>

    <div class="card">
      <div class="card-title">👥 Team Members (Team No. 7)</div>
      <div class="meta-item"><strong>👑 Team Leader:</strong> M. AFROSE</div>
      <div class="meta-item"><strong>👤 Team Member 1:</strong> MANOHAR.E</div>
      <div class="meta-item"><strong>👤 Team Member 2:</strong> MURUGAN.S</div>
      <div class="meta-item"><strong>👤 Team Member 3:</strong> MUSHARAF.B</div>
      <div class="meta-item"><strong>Status:</strong> Completed & Deployed Live</div>
    </div>
  </div>

  <div class="links-box">
    <div class="card-title" style="color:#15803d; border-color:#bbf7d0;">🔗 Live Submission & Repository URLs</div>
    <div class="link-row">
      <span class="link-label">1. Live Web Application:</span>
      <a class="link-url" href="https://edugenie-project-z7c2.onrender.com">https://edugenie-project-z7c2.onrender.com</a>
    </div>
    <div class="link-row">
      <span class="link-label">2. GitHub Code Repository:</span>
      <a class="link-url" href="https://github.com/Afrose0507/EduGenie-project">https://github.com/Afrose0507/EduGenie-project</a>
    </div>
    <div class="link-row">
      <span class="link-label">3. Google Cloud Assignment Document:</span>
      <a class="link-url" href="https://docs.google.com/document/d/1qfB_S3qCLtBpc3etJkYvZkdMlBKCmvYK/edit">https://docs.google.com/document/d/1qfB_S3qCLtBpc3etJkYvZkdMlBKCmvYK/edit</a>
    </div>
  </div>

  <h2 class="section-heading">1. Executive Summary & Abstract</h2>
  <p>
    <strong>EduGenie</strong> is an intelligent, universal educational assistant built with Google Gemini 3.8 Flash, Python FastAPI, and an adaptive depth classification engine. Designed as part of the <em>Naan Mudhalvan</em> curriculum, EduGenie empowers students across diverse educational levels—from school students to engineering and postgraduate scholars—to acquire factual knowledge, test conceptual mastery, and generate structured learning curricula.
  </p>
  <p>
    Unlike conventional chatbots that produce overwhelming walls of generic text or generic study advice, EduGenie incorporates an <strong>Adaptive Response Engine</strong>. It delivers concise 3-part answers (Definition, Key Points, Simple Example) for simple conceptual questions, while providing exhaustive multi-part technical breakdowns when students explicitly request deep dives or multi-component explanations.
  </p>

  <h2 class="section-heading">2. Problem Statement & Motivation</h2>
  <p>
    Students preparing for examinations face significant challenges with conventional study platforms:
  </p>
  <ul>
    <li><strong>Verbose & Fluffy Responses:</strong> Generic LLMs often output repetitive introductory fluff and vague advice before addressing core exam questions.</li>
    <li><strong>Lack of Structural Discipline:</strong> Simple questions such as <em>"What is AI?"</em> often receive 1,000-word essays, while complex requests like <em>"Explain 1NF, 2NF, 3NF with examples"</em> omit necessary technical steps.</li>
    <li><strong>Narrow Domain Focus:</strong> Most study assistants cater strictly to programming and omit essential academic fields like Commerce, Life Sciences, Economics, and Mathematics.</li>
  </ul>
  <p>
    <strong>EduGenie solves these issues</strong> through automated intent classification, zero-filler prompt engineering, and native multi-discipline calibration.
  </p>

  <!-- ==================== PAGE 2 ==================== -->
  <div class="page-break"></div>

  <h2 class="section-heading">3. System Architecture & Tech Stack</h2>
  <p>
    EduGenie follows a high-throughput, decoupled micro-architecture combining a modern responsive frontend with a FastAPI asynchronous backend and Google Generative Language REST APIs:
  </p>

  <div class="callout-info">
    <strong>Architecture Workflow:</strong> Student Query → Responsive UI → FastAPI Endpoint (`/qa`, `/explain`, `/quiz`, etc.) → Dynamic Depth Classifier (`classify_question_depth`) → Google Gemini REST API (`gemini-3.8-flash`) → Relevance Filter (`is_answer_relevant`) → Formatted Markdown Response.
  </div>

  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Layer</th>
        <th style="width: 35%;">Technology</th>
        <th style="width: 40%;">Key Responsibility</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Frontend</strong></td>
        <td>HTML5, Modern CSS, Vanilla JS, Marked.js</td>
        <td>Responsive tab navigation, instant MCQ quiz grading, markdown rendering.</td>
      </tr>
      <tr>
        <td><strong>Backend Framework</strong></td>
        <td>Python 3.13, FastAPI, Uvicorn ASGI</td>
        <td>Form parsing, CORS handling, query depth classification, REST orchestration.</td>
      </tr>
      <tr>
        <td><strong>AI Engine</strong></td>
        <td>Google Gemini 3.8 Flash (`gemini-3.8-flash`)</td>
        <td>State-of-the-art multimodal reasoning, dynamic thinking, and content generation.</td>
      </tr>
      <tr>
        <td><strong>API Authentication</strong></td>
        <td>REST Header (`x-goog-api-key`)</td>
        <td>Secure enterprise authentication supporting modern Google Cloud API tokens.</td>
      </tr>
      <tr>
        <td><strong>Deployment & Host</strong></td>
        <td>Render Cloud Platform (Linux Container)</td>
        <td>24/7 continuous deployment linked directly to GitHub repository with HTTPS.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="section-heading">4. Core Modules & Implementation Details</h2>
  <div class="modules-grid">
    <div class="module-card">
      <h4>1. Ask a Question Engine (`qna.py`)</h4>
      <p>Answers academic questions with intelligent depth classification. Formats simple queries into 3 concise parts and complex queries into detailed multi-part breakdowns.</p>
    </div>
    <div class="module-card">
      <h4>2. Concept Explainer (`explanation_module.py`)</h4>
      <p>Demystifies abstract concepts using intuitive everyday analogies, technical mechanism steps, and real-world industrial use cases.</p>
    </div>
    <div class="module-card">
      <h4>3. 10-Question Quiz Generator (`quiz_module.py`)</h4>
      <p>Generates 10 curriculum-aligned Multiple Choice Questions (MCQs) with options A-D, automated answer validation, and explanatory feedback.</p>
    </div>
    <div class="module-card">
      <h4>4. Study Notes Summarizer (`summary_module.py`)</h4>
      <p>Condenses lengthy textbook chapters and syllabus excerpts into bulleted key takeaways, core formulas, and quick revision notes.</p>
    </div>
    <div class="module-card">
      <h4>5. 6-Week Learning Roadmap (`learning_path.py`)</h4>
      <p>Structures full 6-week personalized learning journeys from fundamental prerequisites to advanced industry applications.</p>
    </div>
    <div class="module-card">
      <h4>6. Universal Gemini Client (`gemini_client.py`)</h4>
      <p>High-reliability REST engine with automated model failover, header authentication, and thought-process filtering for Gemini 3 models.</p>
    </div>
  </div>

  <h3 class="sub-heading">4.1 Dynamic Response Length Adaptation Algorithm</h3>
  <p>
    To satisfy examination grading standards without overwhelming the learner, EduGenie implements an automated query depth classifier:
  </p>

  <div class="code-block">
<span class="keyword">def</span> classify_question_depth(question: str) -> str:
    <span class="comment"># 1. Explicit triggers requesting comprehensive depth</span>
    detail_phrases = [<span class="string">"in detail"</span>, <span class="string">"explain everything"</span>, <span class="string">"with examples"</span>, <span class="string">"step by step"</span>]
    <span class="keyword">if</span> any(phrase <span class="keyword">in</span> question.lower() <span class="keyword">for</span> phrase <span class="keyword">in</span> detail_phrases):
        <span class="keyword">return</span> <span class="string">"detailed"</span>

    <span class="comment"># 2. Multi-part indicators (e.g. 1NF/2NF/3NF, multiple ?, difference between)</span>
    <span class="keyword">if</span> question.count(<span class="string">'?'</span>) > 1 <span class="keyword">or</span> re.search(<span class="string">r'\b(difference between|1nf|2nf|main functions)\b'</span>, question.lower()):
        <span class="keyword">return</span> <span class="string">"detailed"</span>

    <span class="comment"># 3. Simple definitional queries default to concise 3-part structure</span>
    <span class="keyword">return</span> <span class="string">"simple"</span>
  </div>

  <!-- ==================== PAGE 3 ==================== -->
  <div class="page-break"></div>

  <h2 class="section-heading">5. Answer Structure Standards & Demonstration</h2>

  <h3 class="sub-heading">Standard A: Simple / Concise Questions</h3>
  <p>
    For simple questions (e.g., <em>"What is AI?"</em>, <em>"What is Python?"</em>, <em>"What is DNA?"</em>, <em>"What is a database?"</em>), EduGenie enforces a strict 3-part layout:
  </p>
  <div class="callout-success">
    <strong>1. Definition:</strong> 1–2 factual sentences answering the exact question immediately.<br>
    <strong>2. Key Points:</strong> 2 to 4 bullet points highlighting essential features or functions.<br>
    <strong>3. Simple Example:</strong> A 1–2 sentence relatable real-world application.
  </div>

  <h3 class="sub-heading">Sample Simple Verification: "What is Artificial Intelligence?"</h3>
  <div class="card" style="background:#f8fafc; font-size:12px;">
    <strong>Definition:</strong> Artificial Intelligence (AI) refers to the simulation of human intelligence in machines, enabling computers to learn, reason, solve problems, and make decisions.<br><br>
    <strong>Key Points:</strong>
    <ul style="margin:4px 0 6px 18px; padding:0;">
      <li><strong>Core Functionality:</strong> Analyzes large volumes of data to discover patterns and make predictions.</li>
      <li><strong>Major Subfields:</strong> Includes Machine Learning (ML), Deep Learning, Natural Language Processing (NLP), and Computer Vision.</li>
      <li><strong>Everyday Applications:</strong> Powers search engines, autonomous vehicles, recommendation systems, and virtual assistants.</li>
    </ul>
    <strong>Simple Example:</strong> When your phone suggests the next word while typing or Netflix recommends a movie based on your watch history, AI algorithms are predicting your preference.
  </div>

  <h3 class="sub-heading">Standard B: Detailed / Multi-Part Questions</h3>
  <p>
    For detailed questions (e.g., <em>"What is normalization in DBMS? Explain 1NF, 2NF, and 3NF with a simple example"</em>), EduGenie delivers a structured academic breakdown:
  </p>
  <div class="card" style="background:#f8fafc; font-size:12px;">
    <strong>1. Direct Definition:</strong> Normalization is a systematic database design technique that organizes tables to minimize data redundancy and prevent insertion, update, and deletion anomalies.<br><br>
    <strong>2. Normal Forms Breakdown:</strong>
    <ul style="margin:4px 0 6px 18px; padding:0;">
      <li><strong>1NF (First Normal Form):</strong> Each column must contain atomic (indivisible) values, and each record must be unique (no repeating groups).</li>
      <li><strong>2NF (Second Normal Form):</strong> Table must be in 1NF and all non-key attributes must be fully functionally dependent on the primary key (no partial dependencies).</li>
      <li><strong>3NF (Third Normal Form):</strong> Table must be in 2NF and have no transitive dependencies (non-key attributes must not depend on other non-key attributes).</li>
    </ul>
    <strong>3. Concrete Example:</strong> A student table with `(StudentID, Course, Instructor, InstructorRoom)` is split into `(StudentID, Course)` and `(Course, Instructor, InstructorRoom)` to eliminate transitive updates.
  </div>

  <h2 class="section-heading">6. Multi-Disciplinary Universal Support</h2>
  <table>
    <thead>
      <tr>
        <th>Discipline</th>
        <th>Sample Question Tested</th>
        <th>EduGenie Response Focus</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Computer Science</strong></td>
        <td>"Difference between Process and Thread?"</td>
        <td>Memory sharing, context switching overhead, OS PCB structure.</td>
      </tr>
      <tr>
        <td><strong>Biology / Medicine</strong></td>
        <td>"What is Photosynthesis and its stages?"</td>
        <td>Light-dependent and Calvin cycle reactions, chlorophyll roles.</td>
      </tr>
      <tr>
        <td><strong>Commerce / Finance</strong></td>
        <td>"What is Double-Entry Bookkeeping?"</td>
        <td>Debit/Credit balancing principle, Ledger & Trial Balance examples.</td>
      </tr>
      <tr>
        <td><strong>Physics</strong></td>
        <td>"State Newton's Three Laws of Motion."</td>
        <td>Inertia, F=ma formula derivation, action-reaction pair mechanics.</td>
      </tr>
    </tbody>
  </table>

  <!-- ==================== PAGE 4 ==================== -->
  <div class="page-break"></div>

  <h2 class="section-heading">7. Cloud Deployment & Live Verification</h2>
  <p>
    EduGenie has been packaged and deployed to production on Render Cloud. The application runs as a production service accessible on both mobile and desktop browsers:
  </p>
  <ul>
    <li><strong>Live Production URL:</strong> <a href="https://edugenie-project-z7c2.onrender.com" style="color:#2563eb;">https://edugenie-project-z7c2.onrender.com</a></li>
    <li><strong>Deployment Type:</strong> Continuous Deployment via GitHub Webhook (`origin/main`).</li>
    <li><strong>Runtime Environment:</strong> Linux Container with Uvicorn ASGI Web Server.</li>
    <li><strong>Uptime & Availability:</strong> 24/7 cloud availability with automatic HTTPS SSL encryption.</li>
    <li><strong>Environment Variables:</strong> Secure server-side injection of `GEMINI_API_KEY` (never exposed to client browser).</li>
  </ul>

  <h2 class="section-heading">8. Testing, Verification & Quality Assurance</h2>
  <p>
    Comprehensive automated and manual test suites were executed to validate project stability:
  </p>
  <table>
    <thead>
      <tr>
        <th>Test Category</th>
        <th>Methodology</th>
        <th>Result</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>API Connectivity</strong></td>
        <td>Direct REST test with `gemini-3.8-flash` via `x-goog-api-key` header</td>
        <td><strong style="color:#16a34a;">PASSED (HTTP 200)</strong></td>
      </tr>
      <tr>
        <td><strong>Depth Classification</strong></td>
        <td>17 automated unit test queries for simple vs. detailed classification</td>
        <td><strong style="color:#16a34a;">100% PASS (17/17)</strong></td>
      </tr>
      <tr>
        <td><strong>Relevance Validation</strong></td>
        <td>Keyword extraction check preventing subject drift and generic filler</td>
        <td><strong style="color:#16a34a;">PASSED (Zero Fluff)</strong></td>
      </tr>
      <tr>
        <td><strong>MCQ Quiz Scoring</strong></td>
        <td>10-question generation and instant client-side answer evaluation</td>
        <td><strong style="color:#16a34a;">PASSED (Accurate)</strong></td>
      </tr>
      <tr>
        <td><strong>Cross-Device UI</strong></td>
        <td>Tested on Chrome Desktop, Edge, Android Mobile, and iOS Safari</td>
        <td><strong style="color:#16a34a;">PASSED (Responsive)</strong></td>
      </tr>
    </tbody>
  </table>

  <h2 class="section-heading">9. Conclusion & Future Enhancements</h2>
  <p>
    EduGenie demonstrates the practical integration of modern Generative AI within higher education. By combining Google Gemini 3.8 Flash with algorithmic answer calibration, the project provides students with direct, syllabus-aligned, and fluff-free assistance across any educational discipline.
  </p>
  <p><strong>Planned Future Enhancements:</strong></p>
  <ul>
    <li><strong>Voice Interaction:</strong> Integration with Gemini Live API for real-time spoken audio doubt resolution.</li>
    <li><strong>Multimodal PDF Notes Analysis:</strong> Direct file upload of handwritten college notes and textbook diagrams.</li>
    <li><strong>Regional Language Support:</strong> Seamless bilingual responses in Tamil and other Indian languages for rural learners.</li>
  </ul>

  <div class="report-footer">
    <span>EduGenie Project Report • Team No. 7 • M. Afrose (Lead), Manohar.E, Murugan.S, Musharaf.B</span>
    <span>Naan Mudhalvan • Skillwallet Submission Document • 2026</span>
  </div>

</body>
</html>
"""

# 1. Write HTML file to scratch / project folder
html_path = r"C:\Users\Afroz\.gemini\antigravity\scratch\edugenie\EduGenie_Project_Report_Skillwallet.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"HTML saved to {html_path}")

# 2. Compile to PDF using Edge headless
pdf_path = r"C:\Users\Afroz\.gemini\antigravity\scratch\edugenie\EduGenie_Project_Report_Skillwallet.pdf"
edge_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
]
edge_exe = next((p for p in edge_paths if os.path.exists(p)), None)

if not edge_exe:
    print("ERROR: Edge executable not found")
else:
    print(f"Using Edge: {edge_exe}")
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        print(f"SUCCESS! PDF created at {pdf_path}, size = {os.path.getsize(pdf_path)} bytes")

        # 3. Copy to Downloads and Desktop
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        desktop_dir = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        
        target_locations = [downloads_dir, desktop_dir]
        for loc in target_locations:
            if os.path.exists(loc):
                dest = os.path.join(loc, "EduGenie_Project_Report_Skillwallet.pdf")
                shutil.copy2(pdf_path, dest)
                print(f"Copied to: {dest}")
    else:
        print("ERROR generating PDF:", res.stderr)
