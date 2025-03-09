# AI Student Helper

## 1. Introduction
AI Student Helper is a **multi-agent automation system** built with **LangGraph** and **LangChain** to assist students and professionals in automating academic and career-related tasks. It follows a **graph-based workflow execution model**, ensuring efficient **task routing and execution**.

---

## 2. System Architecture
The AI Student Helper follows a **modular multi-agent architecture**, where:
- A **Supervisor Agent** acts as a **task router**.
- **Specialized Agents** execute specific tasks based on **user input**.
- A **graph-based workflow (LangGraph)** dynamically determines **execution paths**.

### **2.1 High-Level Diagram**
```
+------------------+    
|  User Request   |    
+------------------+    
         |      
         v      
+---------------------+    
|  Supervisor Agent  |    
+---------------------+    
         |      
 ------------------------------------
 |                |                |
 v                v                v
+---------+    +---------+    +---------+
| PDF     |    | YouTube |    | Job     |
| Agent   |    | Agent   |    | Agent   |
+---------+    +---------+    +---------+
         |
         v
+------------------+
|  Homework Agent  |
+------------------+
```

---

## **3. Key Components**

### **3.1 Supervisor Agent**
- **Role**: Routes user requests to the correct specialized agent.
- **Logic**:
  - **Analyzes user input** using an **LLM**.
  - **Keyword-based mapping** triggers corresponding agents.
  - **Returns processed results** to the user.

### **3.2 Specialized Agents**

Each agent operates independently, executing tasks based on **LLM processing, automation scripts, and external API interactions**.

#### **📄 PDF Summarizer (`pdf_agent`)**
- **Prompts** the user for a PDF file path.
- **Extracts text content** using `PyMuPDF` or `pdfplumber`.
- Uses an **LLM-based summarization function** to generate key points.
- **Returns a structured summary**.

#### **🎥 YouTube Video Summarizer (`youtube_agent`)**
- Uses `pytube` to **download transcripts** (if available).
- If no transcript is available, leverages **Whisper for speech-to-text conversion**.
- Summarizes content using **LangGraph-based AI model**.

#### **💼 Job Application Assistant (`job_agent`)**
- Extracts **resume information**.
- Uses `Selenium` or `LinkedIn API` to **automate job applications**.
- Matches jobs based on **LLM-powered profile analysis**.

#### **📚 Homework Helper (`homework_agent`)**
- Uses **Streamlit** for an **interactive UI**.
- Implements **LLM-based step-by-step problem-solving**.
- Provides **explainable responses** for better understanding.

---

## **4. Technologies Used**

| **Technology** | **Role** |
|--------------|----------|
| Python | Core programming language |
| LangGraph | Manages workflow execution |
| ChatOpenAI | Provides AI-powered responses |
| Streamlit | Enables interactive UI |
| Selenium | Automates job applications |
| pytube | Extracts YouTube video transcripts |
| PyMuPDF | Parses PDF files |

---

## **5. Workflow Execution**

### **5.1 Request Handling Flow**
1. **User enters a request** (e.g., `"summarize a PDF"`).
2. **Supervisor Agent extracts intent**.
3. **Relevant agent is activated**.
4. **Task is processed, and output is generated**.
5. **Response is returned to the user**.

### **5.2 Graph Execution with LangGraph**
- Each **node in the graph** represents an **agent**.
- The **edges define execution logic** based on user input.
- This structure allows **dynamic branching without unnecessary processing**.

---

## **6. Deployment**

### **6.1 Local Setup**

#### **Prerequisites**
- Python **3.8+**
- OpenAI API Key
- Required Python libraries

#### **Installation Steps**
1. **Clone the repository**:
   ```sh
   git clone https://github.com/your-repo/ai-student-helper.git
   cd ai-student-helper
   ```

2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```sh
   python3 SupervisorLangGraph.py
   ```

#### **Environment Setup**
- Set the OpenAI API key:
  ```sh
  export OPENAI_API_KEY="your_open_ai_key"
  ```
- Configure LinkedIn credentials in `config.yml`.
- Execute the main script:
  ```sh
  python3 SupervisorLangGraph.py
  ```

---

## **7. Demo Videos**
Demo videos are available in the following directory:
```
https://github.com/nselvar/AIStudentHelper/tree/main/demo
```

---

## **8. Conclusion**
The **AI Student Helper** is a **multi-agent automation system** that efficiently handles **student and professional tasks** using **AI-based interactions**. It leverages **LangGraph**, **LangChain**, and **LLM-powered processing** to automate complex workflows.

---
