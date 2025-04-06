<div style="text-align: center; font-family: Arial, sans-serif;">
<strong>RAG Architecture</strong><br/>
  <img 
    src="https://github.com/user-attachments/assets/1b648d60-58cc-4b95-a951-447b603140fc" 
    alt="RAG Architecture" 
    style="max-width: 100%; height: auto; margin-bottom: 16px;"
  />

## 🧠 Architecture Overview

The architecture follows a **modular and scalable RAG (Retrieval-Augmented Generation)** design tailored for a learning management environment. Here’s how it works:

### 📂 FTP Upload + Processing (Teacher Side)
- Teachers upload study materials (PDFs, PPTs, Docs) to an **FTP Server (AWS S3)**.
- Files are processed through a **chunking and embedding pipeline**, converting them into vector embeddings.
- These embeddings are stored in a **Vector Database**, making them retrievable based on student queries.

### 📚 RAG Core (Retriever + Generator)
- When students ask questions or request notes, the system:
  - Sends the query to the **retriever system** that fetches the most relevant embedded chunks.
  - These are passed to an **LLM (Gemini 1.5 Pro)** which generates accurate, contextual responses.
- The RAG system ensures answers are **grounded in teacher-uploaded content**.

### 👨‍🎓 Student Panel Functions
- **Notes Query:** Get simplified, to-the-point notes from vast documents.
- **Quizzes:** Generate level-specific quizzes (Easy/Medium/Hard).
- **Concept Visualization:** Converts complex concepts into easy-to-understand formats using LLMs.

### 👨‍🏫 Teacher Panel Functions
- **PPT Generation:** Upload syllabus/content and generate high-quality presentations.
- **Custom Question Papers:** Generate questions based on topic, difficulty, and marks.
- **Question Banks:** Bulk generation of MCQs for practice sets.



  <div style="font-size: 16px; margin-top: 24px;">
    <strong>Contributor</strong><br/>
    <a href="https://github.com/altamsh04" target="_blank">altamsh04</a><br/>
    <a href="https://github.com/shardulmore112" target="_blank">shardulMore112</a>
  </div>
</div>
